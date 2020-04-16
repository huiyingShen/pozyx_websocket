
from time import time,sleep
import numpy as np
# from pypozyx import (PozyxSerial, PozyxConstants, version,
#                      SingleRegister, DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, get_first_pozyx_serial_port)

from pypozyx import (SensorData, SingleRegister, POZYX_SUCCESS, get_first_pozyx_serial_port,
                     PozyxSerial, get_serial_ports,DeviceRange,PozyxConstants,DeviceCoordinates,POZYX_3D, Coordinates)
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU
from pypozyx.structures.device import UWBSettings

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

class IndoorNav(object):

    def __init__(self):
        self.serial_port = get_first_pozyx_serial_port()
        self.pozyx = PozyxSerial(self.serial_port)
        self.position = Coordinates()

        # self.ax = ax
        # self.dt = dt
        # self.maxt = maxt
        # self.tdata = [0]
        # self.ydata = [0]
        # self.line = Line2D(self.tdata, self.ydata)
        # self.ax.add_line(self.line)
        # self.ax.set_ylim(-.1, 1.1)
        # self.ax.set_xlim(0, self.maxt)

    # def update(self, y):
    #     lastt = self.tdata[-1]
    #     if lastt > self.tdata[0] + self.maxt:  # reset the arrays
    #         self.tdata = [self.tdata[-1]]
    #         self.ydata = [self.ydata[-1]]
    #         self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
    #         self.ax.figure.canvas.draw()

    #     t = self.tdata[-1] + self.dt
    #     self.tdata.append(t)
    #     self.ydata.append(y)
    #     self.line.set_data(self.tdata, self.ydata)
    #     return self.line,
        
    def getDist(self,destination, remote = None,nAverage=5):
        n = 0
        sm = 0
        ranging_protocol = PozyxConstants.RANGE_PROTOCOL_PRECISION
        # ranging_protocol = PozyxConstants.RANGE_PROTOCOL_FAST
        for i in range(nAverage):
            self.pozyx.setRangingProtocol(ranging_protocol, remote)
            device_range = DeviceRange()
            status = self.pozyx.doRanging(destination, device_range, remote)
            if status == POZYX_SUCCESS:
                # print('   ',self.device_range.distance)
                sm += device_range.distance
                n += 1
        print('   n = ',n)
        return int(sm/n)

    def setAllAnchorIds(self,a0,a1,a2,a3):
        self.anchorIds = a0,a1,a2,a3
        return self

    def getAllDist(self):
        for i in range(4):
            i1 = (i+1)%4
            print(self.getDist(self.anchorIds[i],remote = self.anchorIds[i1]))

        return self
    
    def addAllAnchors(self,id_xyz):
        self.anchorsPlusXyz = []
        for id,x,y,z in id_xyz:
            self.anchorsPlusXyz.append(DeviceCoordinates(id, 1, Coordinates(x,y,z)))

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
        dimension = PozyxConstants.DIMENSION_3D
        algorithm = PozyxConstants.POSITIONING_ALGORITHM_UWB_ONLY
        ranging_protocol = PozyxConstants.RANGE_PROTOCOL_FAST
        
        status = self.pozyx.doPositioning(self.position, dimension, height=0, algorithm=algorithm, remote_id=self.remote_id)
        if status == POZYX_SUCCESS:
            # print(position)
            return self.position

        print("doPositioning failed")
        return Coordinates()

        

    def test0(self):
        self.setAllAnchorIds(0x6a31,0x6a35,0x6a60,0x6a6f)
        for i in range(0,4):
            print(hex(self.anchorIds[i]),hex(self.anchorIds[(i+1)%4]))
            d1 = self.getDist(self.anchorIds[i],remote = self.anchorIds[(i+1)%4],nAverage=3)
            d2 = self.getDist(self.anchorIds[(i+1)%4],remote = self.anchorIds[i],nAverage=3)
            print(d1,d2)
        return self

    def test1(self):
        self.setAllAnchorIds(0x6a31,0x6a35,0x6a60,0x6a6f)
        remote = 0x6a31
        destination = 0x6a35
        ranging_protocol = PozyxConstants.RANGE_PROTOCOL_PRECISION
        self.pozyx.setRangingProtocol(ranging_protocol, remote)
        device_range = DeviceRange()
        t0 = time()
        for i in range(1000):
            status = self.pozyx.doRanging(destination, device_range, remote)
        print("time = ", (time()-t0)/1000)
        return self

    def test2(self, id0,id1,dx,dy):
        import math
        d1 = self.getDist(0x6a35,remote = 0x6a60,nAverage=3)
        d2 = self.getDist(0x6a60,remote = 0x6a35,nAverage=3)
        dd = (d1+d2)/2
        # print(dx*dx + dy*dy, dd*dd)
        err = dx*dx + dy*dy - dd*dd
        print(d1,d2)
        print(dx,dy,err,math.sqrt(abs(err)))

    def test3(self):
        def bound(val,low,high):
            if val< low: val = low
            elif val > high: val = high
            return val

        def dist2(x1,y1,x2,y2): return (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)

        def dist(x1,y1,x2,y2): return np.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
        # 0x6a35,0x6a60,0x6a6f,0x6a31
        # id_xy = (0x6a35,0,1385),(0x6a60,1390,0),(0x6a6f,3050,1580),(0x6a31,1495,3320)
        dimension = PozyxConstants.DIMENSION_3D
        # id_xyz = [(0x6a35,0,99.,0),(0x6a60,107.25,2,0),(0x6a6f,210,98.5,0),(0x6a31,108.5,177.75,0),(0x6a6e,36.5,12.25,0)]#(0x6a6e,133.5,38.75,58.75)]
        id_xyz = [(0x6a35,0,99.,0),(0x6a60,107.25,2,0),(0x6a6f,210,98.5,0),(0x6a31,108.5,177.75,0),(0x6a6e,133.5,38.75,58.75)]
        for i,t in zip(range(len(id_xyz)),id_xyz):
            id,x,y,z = t
            id_xyz[i] = id,x*25.4,y*25.4,z*25.4 # in to mm
            print(id_xyz[i])
        anchorsPlusXyz = []
        for id,x,y,z in id_xyz:
            anchorsPlusXyz.append(DeviceCoordinates(id, 1, Coordinates(x,y,z)))
        remote_id = 0x6a37
        remote_id = None
        self.pozyx.setRangingProtocol(PozyxConstants.RANGE_PROTOCOL_FAST,remote_id=remote_id)
        UWB_settings = UWBSettings()
        for id,x,y,z in id_xyz:
            self.pozyx.getUWBSettings(UWB_settings,id)
            print(UWB_settings)
        self.pozyx.getUWBSettings(UWB_settings,None)
        print(UWB_settings)
        settings2 = UWBSettings(2,850,64,64,11.5)
        # self.pozyx.setUWBSettings(settings2)

        self.setAnchorsManual(anchorsPlusXyz,remote_id = remote_id)
        sensor_data = SensorData()
    
        from math import pi
        from time import time
        from tag_plot import TagPozyx
        import path_proc
        from simpleAudioTest import BeeperManager
        import cv2
        import requests

        im = cv2.imread('dist.png')
        cv2.imshow('dt',im)
        cv2.waitKey(1)
        print(im.shape)
        lines = path_proc.procData()

        fMin,fMax,nSample=300,3000,20
        bm = BeeperManager().setAllBeepers(fMin=fMin, fMax=fMax, nSample=nSample, dur=0.02, trim2Zero=True)

        iPlayer = 0
        play_obj = bm.playi(iPlayer).play_obj
        # tag = TagPozyx(r=0.2,tip=2,theta0=339.0/180*pi).preShow()
        
        for i in range(200): _ = self.localize(dimension = dimension) #warm up   

        coef = 0.001     
        t0 = time()  
        t1 = t0   
        nIter =5000
        xs,ys = [],[]
        tmp = t0
        for i in range(nIter):
            position = self.localize(dimension = dimension)
            status = self.pozyx.getAllSensorData(sensor_data, remote_id=remote_id)
            if status == False: continue
            # print('                      ',sensor_data.euler_angles)
            # print("x, y, heading ", position.x, position.y, sensor_data.euler_angles.heading)
            angle = -sensor_data.euler_angles.heading/180*pi
            dt = time() - t1
            t1 = time()
            # t0 = t1
            x,y = position.x*coef, position.y*coef
            xs.append(x)
            ys.append(y)
            if len(xs)>=5:
                xTmp = xs[-5:]
                yTmp = ys[-5:]
                yTmp.sort()
                xTmp.sort()
                x,y = xTmp[2],yTmp[2]
            iy,ix = im.shape[0] - int(y*100),int(x*100)
            ix = bound(ix,0,im.shape[1]-1)
            iy = bound(iy,0,im.shape[0]-1)
            val = 255 - int(im[iy,ix,0])
            iPlayer = int((nSample + 1)*val/255)

            try: r = requests.post('http://127.0.0.1:8000/xyz', data ={'x':ix,'y':iy,'z':iPlayer}) 
            except: pass
             # iVal = int(np.abs(x-5*0.3048)*100)
            # a = angle
            # if a < 0: a += pi*2
            # iPlayer = int(bound(a,0,pi*2)*nSample/pi/2)
            # iPlayer = int(bound(iVal,0,50)*nSample/50)
            # print("angle= {:6.4f}, a= {:6.4f}, iPlayer = {:6.4f}  ".format( sensor_data.euler_angles.heading, a, iPlayer))
            print("dt = {:6.4f}, x = {:6.4f}, y = {:6.4f}, iPlayer = {}".format(dt,x,y,iPlayer))
            # if time()-tmp>0.03:
            # bm.playi(iPlayer).play_obj
                # tmp = time()

        #     tag.cla()
        #     tag.plot_lines(lines)
        #     tag.text(0.1,5.5,'{:6.3f}fps'.format(1.0/dt))
        #     tag.text(x,y,'({:6.3f},{:6.3f})'.format(x,y))
        #     tag.rotTrn(x,y,angle).setLim().draw().pause(0.01)
        #     # print(sensor_data.euler_angles.heading)

        dt = (time() - t0)/nIter
        print('fps = ',1/dt)
        print(' ')
        x0,y0 = 5*0.3048, 10*0.3048
        x1,y1 = np.average(xs),np.average(ys)
        d0,d2 = [],[]
        for x,y in zip(xs,ys):
            d0.append(dist(x,y,x0,y0)) 
            d2.append(dist(x,y,x1,y1))
        # d2 = np.sort(d2) 
        # np.min(d2),np.max(d2),np.median(d2)
        # mid = int(len(d2)/2)
        # print('min, max, median: {:6.4f}, {:6.4f}, {:6.4f}'.format(d2[0],d2[-1],d2[mid]))
        print('runs = {}'.format(len(d2)))
        print('measured tag (x,y):    {:6.4f}, {:6.4f}'.format(x0,y0))
        print('detected tag centroid: {:6.4f}, {:6.4f}'.format(x1,y1))
        print('distance to centroid: median, min, max: {:6.4f}, {:6.4f}, {:6.4f}'.format(np.median(d2),np.min(d2),np.max(d2)))
        print('distance to measured (x,y): median, min, max: {:6.4f}, {:6.4f}, {:6.4f}'.format(np.median(d0),np.min(d0),np.max(d0)))
        # tag.showAndHold()


    def testSettings(self):
        
        from time import sleep
        from pypozyx.core import PozyxCore
        from pypozyx.definitions import (PozyxBitmasks, PozyxRegisters, PozyxConstants, POZYX_SUCCESS, POZYX_FAILURE,
                                        POZYX_TIMEOUT, ERROR_MESSAGES)
        from pypozyx.structures.device import NetworkID, UWBSettings, DeviceList, Coordinates, RXInfo, DeviceCoordinates, FilterData, AlgorithmData
        from pypozyx.structures.generic import Data, SingleRegister, dataCheck
        from pypozyx.structures.sensor_data import PositioningData, RangeInformation

        from warnings import warn

        remote_id = None

        tmp_data = Data([0] * 4)
        status = self.pozyx.getRead(PozyxRegisters.UWB_CHANNEL, tmp_data, remote_id)
        settings = UWBSettings()
        settings.load(tmp_data.data)
        
        settings2 = UWBSettings(2,850,64,64,11.5)

        print(tmp_data)


if __name__ == "__main__":
    IndoorNav().test3()
    # IndoorNav().testSettings()
    # Beeper().test0()
