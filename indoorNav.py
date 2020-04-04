
from time import time,sleep
import winsound

# from pypozyx import (PozyxSerial, PozyxConstants, version,
#                      SingleRegister, DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, get_first_pozyx_serial_port)

from pypozyx import (SensorData, SingleRegister, POZYX_SUCCESS, get_first_pozyx_serial_port,
                     PozyxSerial, get_serial_ports,DeviceRange,PozyxConstants,DeviceCoordinates,POZYX_3D, Coordinates)
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU

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

    def update(self, y):
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ydata = [self.ydata[-1]]
            self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax.figure.canvas.draw()

        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.ydata.append(y)
        self.line.set_data(self.tdata, self.ydata)
        return self.line,
        
    def getDist(self,destination, remote = None,nAverage=5):
        n = 0
        sm = 0
        ranging_protocol = PozyxConstants.RANGE_PROTOCOL_PRECISION
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

    def setAnchorsManual(self,remote_id, anchorsPlusXyz):
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

    def localize(self, height = 0 ):
        dimension = PozyxConstants.DIMENSION_3D
        algorithm = PozyxConstants.POSITIONING_ALGORITHM_UWB_ONLY
        
        status = self.pozyx.doPositioning(self.position, dimension, height, algorithm, self.remote_id)
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
        for i in range(4):
            d1 = self.getDist(0x6a31,remote = 0x6a6f,nAverage=1)
            d2 = self.getDist(0x6a6f,remote = 0x6a31,nAverage=1)
            print(d1,d2)
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
        # 0x6a35,0x6a60,0x6a6f,0x6a31
        # id_xy = (0x6a35,0,1385),(0x6a60,1390,0),(0x6a6f,3050,1580),(0x6a31,1495,3320)
        id_xy = [(0x6a35,0,99.25),(0x6a60,108.5,2),(0x6a6f,209,98.5),(0x6a31,108.5,177.5)]
        for i,t in zip(range(len(id_xy)),id_xy):
            id,x,y = t
            id_xy[i] = id,x*25.4,y*25.4 # in to mm
            print(id_xy[i])
        anchorsPlusXyz = []
        for id,x,y in id_xy:
            anchorsPlusXyz.append(DeviceCoordinates(id, 1, Coordinates(x,y,0)))
        remote_id = 0x6a37
        self.setAnchorsManual(None, anchorsPlusXyz)
        sensor_data = SensorData()
        
        from math import pi
        from time import time
        from tag_plot import TagPozyx
        import path_proc
        from simpleAudioTest import BeeperManager
        import cv2

        im = cv2.imread('dist.png')
        cv2.imshow('dt',im)
        print(im.shape)
        lines = path_proc.procData()

        fMin,fMax,nSample=300,3000,10
        bm = BeeperManager().setAllBeepers(fMin=fMin, fMax=fMax, nSample=nSample, dur=0.1, trim2Zero=True)

        iPlayer = 0
        play_obj = bm.playi(iPlayer).play_obj
        tag = TagPozyx(r=0.2,tip=2,theta0=339.0/180*pi).preShow()
        
        coef = 0.001     
        t0 = time()       
        for i in range(150):
            position = self.localize()
            status = self.pozyx.getAllSensorData(sensor_data, remote_id=None)
            if status == False: 
                play_obj.wait_done()
                play_obj = bm.playi(iPlayer).play_obj
                continue
            # print('                      ',sensor_data.euler_angles)
            print("x, y, heading ", position.x, position.y, sensor_data.euler_angles.heading)
            angle = -sensor_data.euler_angles.heading/180*pi
            t1 = time()
            dt = t1 - t0
            t0 = t1
            x,y = position.x*coef, position.y*coef

            play_obj.wait_done()
            iy,ix = im.shape[0] - int(y*100),int(x*100)
            ix = bound(ix,0,im.shape[1]-1)
            iy = bound(iy,0,im.shape[0]-1)
            val = 255 - int(im[iy,ix,0])
            iPlayer = int((nSample + 1)*val/255)
            # print("x, y, angle, dt  =  ", x, y, angle, dt)
            print("dt = {:6.4f}, x = {:6.4f}, y = {:6.4f}, iPlayer = {}".format(dt,x,y,iPlayer))


            play_obj = bm.playi(iPlayer).play_obj


 
            tag.cla()
            tag.plot_lines(lines)
            tag.text(0.1,5.5,'{:6.3f}fps'.format(1.0/dt))
            tag.text(x,y,'({:6.3f},{:6.3f})'.format(x,y))
            tag.rotTrn(x,y,angle).setLim().draw().pause(0.01)
            # print(sensor_data.euler_angles.heading)


        tag.showAndHold()


    

if __name__ == "__main__":
    IndoorNav().test3()
    # Beeper().test0()
