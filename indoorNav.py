

from pypozyx import (SensorData, SingleRegister, POZYX_SUCCESS, get_first_pozyx_serial_port,
                     PozyxSerial, get_serial_ports,DeviceRange,PozyxConstants,DeviceCoordinates,POZYX_3D, Coordinates)
from pypozyx import POZYX_POS_ALG_UWB_ONLY
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU
from pypozyx.structures.device import UWBSettings

from time import time,sleep
import numpy as np
from simpleAudioTest import BeeperManager,getPlayerNew
import cv2
import requests

def bound(val,low,high):
    if val< low: val = low
    elif val > high: val = high
    return val

def dist(x1,y1,x2,y2):
    return np.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

def get_iPlayer(x,y,im,nSample):
    iy,ix = im.shape[0] - int(y*100),int(x*100)
    ix = bound(ix,0,im.shape[1]-1)
    iy = bound(iy,0,im.shape[0]-1)
    val = 255 - int(im[iy,ix,0])
    iPlayer = int((nSample + 1)*val/255)
    return ix,iy,iPlayer


class IndoorNav(object):
    @staticmethod
    def summary(xs, ys, x0 = 5*0.3048, y0 = 10*0.3048):
        x1,y1 = np.average(xs),np.average(ys)
        d0,d2 = [],[]
        for x,y in zip(xs,ys):
            d0.append(dist(x,y,x0,y0)) 
            d2.append(dist(x,y,x1,y1))
        print('runs = {}'.format(len(d2)))
        # print('measured tag (x,y):    {:6.4f}, {:6.4f}'.format(x0,y0))
        print('detected tag centroid: {:6.4f}, {:6.4f}'.format(x1,y1))
        print('distance to centroid: median, min, max: {:6.4f}, {:6.4f}, {:6.4f}'.format(np.median(d2),np.min(d2),np.max(d2)))
        # print('distance to measured (x,y): median, min, max: {:6.4f}, {:6.4f}, {:6.4f}'.format(np.median(d0),np.min(d0),np.max(d0)))

    def __init__(self):
        self.serial_port = get_first_pozyx_serial_port()
        self.pozyx = PozyxSerial(self.serial_port)
        self.position = Coordinates()

    def setAnchorsManual(self,anchorsPlusXyz, remote_id= None):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        self.remote_id = remote_id
        status = self.pozyx.clearDevices(remote_id = remote_id)
        for anchor in anchorsPlusXyz:
            status &= self.pozyx.addDevice(anchor, remote_id=remote_id)
        if len(anchorsPlusXyz) > 4:
            status &= self.pozyx.setSelectionOfAnchors(PozyxConstants.ANCHOR_SELECT_AUTO, len(anchorsPlusXyz),
                                                       remote_id=remote_id)
        self.status = status
        return self

    def localize(self,dimension = PozyxConstants.DIMENSION_3D):
        algorithm = PozyxConstants.POSITIONING_ALGORITHM_UWB_ONLY     
        # algorithm = POZYX_POS_ALG_UWB_ONLY
        status = self.pozyx.doPositioning(self.position, dimension, height=0, algorithm=algorithm, remote_id=self.remote_id)
        if status == POZYX_SUCCESS: 
            return self.position
        else:
            print("doPositioning failed")
            return Coordinates()

    def testSettings(self):
        from time import sleep
        from pypozyx.core import PozyxCore
        from pypozyx.definitions import (PozyxBitmasks, PozyxRegisters, PozyxConstants, POZYX_SUCCESS, POZYX_FAILURE,
                                        POZYX_TIMEOUT, ERROR_MESSAGES)
        from pypozyx.structures.device import NetworkID, UWBSettings, DeviceList, Coordinates, RXInfo, DeviceCoordinates, FilterData, AlgorithmData
        from pypozyx.structures.generic import Data, SingleRegister, dataCheck
        from pypozyx.structures.sensor_data import PositioningData, RangeInformation
        remote_id = None
        tmp_data = Data([0] * 4)
        status = self.pozyx.getRead(PozyxRegisters.UWB_CHANNEL, tmp_data, remote_id)
        settings = UWBSettings()
        settings.load(tmp_data.data)
        settings2 = UWBSettings(2,850,64,64,11.5)
        print(tmp_data)

        # UWB_settings = UWBSettings()
        # for id,x,y,z in id_xyz:
        #     self.pozyx.getUWBSettings(UWB_settings,id)
        #     print(UWB_settings)
        # self.pozyx.getUWBSettings(UWB_settings,None)
        # print(UWB_settings)
        # settings2 = UWBSettings(2,850,64,64,11.5)
        # self.pozyx.setUWBSettings(settings2)

    def test3(self,is3d = True, isRemote =True, hasAudio = False, hasSmoothing = True, nIter =100 ):
        if is3d: dimension = PozyxConstants.DIMENSION_3D
        else: dimension = PozyxConstants.DIMENSION_2D
        if isRemote: remote_id = 0x6a37
        else: remote_id = None

        # id_xyz = [(0x6a35,0,99.,0),(0x6a60,107.25,2,0),(0x6a6f,210,98.5,0),(0x6a31,108.5,177.75,0),(0x6a6e,133.5,38.75,58.75)]
        # id_xyz = [(id,x*25.4,y*25.4,z*25.4) for id,x,y,z in id_xyz]
        id_xyz = [(0x6a6f,10,2520,0),(0x6a35,2810,50,0),(0x6a31,5460,3030,0),(0x6a60,2510,4750,0)]
        # id_xyz = [(0x6a6f,3426,0,0),(0x6a35,10,4513,0),(0x6a31,3420-80,12116,0),(0x6a60,6434,8154,0)]
     
        anchorsPlusXyz = [DeviceCoordinates(id, 1, Coordinates(x,y,z)) for id,x,y,z in id_xyz ]

        # self.pozyx.setRangingProtocol(PozyxConstants.RANGE_PROTOCOL_FAST,remote_id=remote_id)
        self.setAnchorsManual(anchorsPlusXyz,remote_id = remote_id)
        sensor_data = SensorData()
    
        # im = cv2.imread('dist.png')
        im = cv2.imread('output.bmp')
        print('im.shape = ', im.shape)

        # fMin,fMax,nSample = 300,3000,20
        # bm = BeeperManager().setAllBeepers(fMin=fMin, fMax=fMax, nSample=nSample, dur=0.02, trim2Zero=True)
        for _ in range(200): _ = self.localize(dimension = dimension) #warm up   

        coef = 0.001     
        t0 = time()    
        if hasSmoothing: nIter += 4
        xs,ys = [],[]
        xSmoothed, ySmoothed = [],[]
        for _ in range(nIter):
            t1 = time()
            position = self.localize(dimension = dimension)
            status = self.pozyx.getAllSensorData(sensor_data, remote_id=remote_id)
            if status == False: continue
            x,y = position.x*coef, position.y*coef
            xs.append(x)
            ys.append(y)
            if hasSmoothing:
                if len(xs)>=5: #x,y = medianFilter(xs,ys)
                    x = np.median(np.array(xs[-5:]))
                    y = np.median(np.array(ys[-5:]))
                    xSmoothed.append(x)
                    ySmoothed.append(y)
            iy,ix = im.shape[0] - int(y*100),int(x*100)
            ix = bound(ix,0,im.shape[1]-1)
            iy = bound(iy,0,im.shape[0]-1)
            val = int(im[iy,ix,0])
            if val == 255 :iPlayer = 0
            else: 
                iPlayer = int(6 - val/40)
            
            # ix,iy,iPlayer = get_iPlayer(x,y,im,nSample)

            heading = int(sensor_data.euler_angles.heading - 223)
            try: r = requests.post('http://127.0.0.1:8000/xyz', data ={'x':ix,'y':iy,'z': heading}) 
            except: pass
            # angle = -sensor_data.euler_angles.heading/180*np.pi
            # a = angle
            # if a < 0: a += pi*2
            # iPlayer = int(bound(a,0,pi*2)*nSample/pi/2)
            # print("angle= {:6.4f}, a= {:6.4f}, iPlayer = {:6.4f}  ".format( sensor_data.euler_angles.heading, a, iPlayer))
            print("dt = {:6.4f}, x = {:6.4f}, y = {:6.4f}, heading = {}".format(time()-t1,x,y,heading))
            if hasAudio: bm.playi(iPlayer)
        print('hasSmoothing = ', hasSmoothing)
        print('fps = {}'.format(nIter/(time() - t0))) 
        if hasSmoothing:self.summary(xSmoothed, ySmoothed, x0 = 2.5, y0 = 2.5 )
        else: self.summary(xs, ys, x0 = 2.5, y0 = 2.5 )

    def testDirection(self,remote_id = 0x6a37):
        sensor_data = SensorData()
        for _ in range(40):
            status = self.pozyx.getAllSensorData(sensor_data, remote_id=remote_id)
            if status:
                h = sensor_data.euler_angles.heading
                r = sensor_data.euler_angles.roll
                p = sensor_data.euler_angles.pitch
                print(" heading = {:6.4f}, roll = {:6.4f}, pitch = {:6.4f}".format(h,r,p))
                sleep(0.1)


if __name__ == "__main__":
    # IndoorNav().testDirection( remote_id = 0x6a37)
    IndoorNav().test3(is3d = True, isRemote = False, hasAudio = False, hasSmoothing=False,nIter = 5000 )

