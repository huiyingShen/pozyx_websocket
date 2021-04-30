#!/usr/bin/env python
"""
The Pozyx ready to localize tutorial (c) Pozyx Labs
Please read the tutorial that accompanies this sketch:
https://www.pozyx.io/Documentation/Tutorials/ready_to_localize/Python

This tutorial requires at least the contents of the Pozyx Ready to Localize kit. It demonstrates the positioning capabilities
of the Pozyx device both locally and remotely. Follow the steps to correctly set up your environment in the link, change the
parameters and upload this sketch. Watch the coordinates change as you move your device around!
"""
from time import sleep,time
from pypozyx import SensorData
from pypozyx import (POZYX_POS_ALG_UWB_ONLY, POZYX_3D, Coordinates, POZYX_SUCCESS, PozyxConstants, version,
                     DeviceCoordinates, PozyxSerial, get_first_pozyx_serial_port, SingleRegister, DeviceList, PozyxRegisters)
# from pythonosc.udp_client import SimpleUDPClient

from pypozyx.tools.version_check import perform_latest_version_check


class ReadyToLocalize(object):
    """Continuously calls the Pozyx positioning function and prints its position."""

    def __init__(self, pozyx, anchors, algorithm=POZYX_POS_ALG_UWB_ONLY, dimension=POZYX_3D, height=1000, remote_id=None):
        self.pozyx = pozyx
        self.anchors = anchors
        self.algorithm = algorithm
        self.dimension = dimension
        self.height = height
        self.remote_id = remote_id

    def setup(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        print("------------POZYX POSITIONING V{} -------------".format(version))
        print("")
        print("- System will manually configure tag")
        print("")
        print("- System will auto start positioning")
        print("")
        if self.remote_id is None:
            self.pozyx.printDeviceInfo(self.remote_id)
        else:
            for device_id in [None, self.remote_id]:
                self.pozyx.printDeviceInfo(device_id)
        print("")
        print("------------POZYX POSITIONING V{} -------------".format(version))
        print("")

        self.setAnchorsManual(save_to_flash=False)


    def loop(self):
        """Performs positioning and displays/exports the results."""
        position = Coordinates()
        sensor_data = SensorData()
        status = self.pozyx.doPositioning(
            position, self.dimension, self.height, self.algorithm, remote_id=self.remote_id)
        status2 = self.pozyx.getAllSensorData(sensor_data, remote_id=self.remote_id)
        if status == POZYX_SUCCESS and status2 == True:
            # self.printPublishPosition(position)
            return position,sensor_data
        else:
            return "error in localizing"



    def setAnchorsManual(self, save_to_flash=False):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        status = self.pozyx.clearDevices(remote_id=self.remote_id)
        for anchor in self.anchors:
            status &= self.pozyx.addDevice(anchor, remote_id=self.remote_id)
        if len(self.anchors) > 4:
            status &= self.pozyx.setSelectionOfAnchors(PozyxConstants.ANCHOR_SELECT_AUTO, len(self.anchors),
                                                       remote_id=self.remote_id)

        if save_to_flash:
            self.pozyx.saveAnchorIds(remote_id=self.remote_id)
            self.pozyx.saveRegisters([PozyxRegisters.POSITIONING_NUMBER_OF_ANCHORS], remote_id=self.remote_id)
        return status

done = False
tMax = 5*60

def test0(send_conn, remote_id = 0x6a37, check_pypozyx_version = True):
    import numpy as np
    global done, tMax

    t0 = time()
    x,y,theta = 100.1,200.2,0
    while not done and time() - t0 <tMax:
        print("done = ",done)
        sleep(0.999)
        x += np.random.random()*10 - 3
        y += np.random.random()*10 - 2
        theta += np.random.random()*10
        theta = theta%360
        send_conn.send((x,y,theta))
        # s = "{:6.3f}  {:6.3f} {:6.3f}  ".format(x,y,theta)

    print("done = ",done)
    send_conn.close()



def main(send_conn, remote_id = 0x6a37, check_pypozyx_version = True):
# def main( remote_id = 0x6a37, check_pypozyx_version = True):
    import requests

    # Check for the latest PyPozyx version. Skip if this takes too long or is not needed by setting to False.
    
    if check_pypozyx_version:
        perform_latest_version_check()

    # shortcut to not have to find out the port yourself
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    remote_id = remote_id                 # remote device network ID


    # necessary data for calibration, change the IDs and coordinates yourself according to your measurement
    # anchors = [DeviceCoordinates(0x6a31, 1, Coordinates(150, 1500, 1540)),
    #            DeviceCoordinates(0x6a60, 1, Coordinates(2180, 0, 1540)),
    #            DeviceCoordinates(0x6a35, 1, Coordinates(3570, 1500, 1540)),
    #            DeviceCoordinates(0x606f, 1, Coordinates(2160, 3050, 1540))] 
    # id_xyz = [(0x6a6f,10,2520,0),(0x6a35,2810,50,0),(0x6a31,5460,3030,0),(0x6a60,2510,4750,0)]

    # anchors = [DeviceCoordinates(0x6a31, 1, Coordinates(5460,   3030,   1540)),
    #            DeviceCoordinates(0x6a60, 1, Coordinates(2510,   4750,   1540)),
    #            DeviceCoordinates(0x6a35, 1, Coordinates(2810,   50,     1540)),
    #            DeviceCoordinates(0x606f, 1, Coordinates(10,     2520,   1540))]
    anchors = [DeviceCoordinates(0x6a31, 1, Coordinates(6000,   3000,   1540)),
               DeviceCoordinates(0x6a60, 1, Coordinates(3000,   6000,   1540)),
               DeviceCoordinates(0x6a35, 1, Coordinates(3000,  0,     1540)),
               DeviceCoordinates(0x606f, 1, Coordinates(0,     3000,   1540))]

    # positioning algorithm to use, other is PozyxConstants.POSITIONING_ALGORITHM_TRACKING
    algorithm = PozyxConstants.POSITIONING_ALGORITHM_UWB_ONLY
    # positioning dimension. Others are PozyxConstants.DIMENSION_2D, PozyxConstants.DIMENSION_2_5D
    dimension = PozyxConstants.DIMENSION_3D
    # height of device, required in 2.5D positioning
    height = 1000

    pozyx = PozyxSerial(serial_port)
    r = ReadyToLocalize(pozyx, anchors, algorithm, dimension, height, remote_id)
    r.setup()
    from time import time
    for _ in range(5000):
        t = time()
        try:
            pos,sensor_data = r.loop()
            heading = int(sensor_data.euler_angles.heading)
            # send_conn.send((pox.x,pos.y,heading))
        except: continue

        # try: _ = requests.post('http://127.0.0.1:8000/xyz', data ={'x':int(pos.x),'y':int(pos.y),'z': heading}) 
        # except: pass

        try:print("0x%0.4x"%remote_id, " dt: {:6.4f}, x(mm): {} y(mm): {} heading: {} ".format(time()-t,pos.x,pos.y,heading ))
        except: pass
        send_conn.send((pos.x,pos.y,heading))

if __name__ == "__main__":
    main()