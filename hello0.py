
from time import time,sleep
import winsound

from pypozyx import SensorData, SingleRegister, POZYX_SUCCESS, get_first_pozyx_serial_port, PozyxSerial, get_serial_ports
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU

# shortcut to not have to find out the port yourself
serial_port = get_first_pozyx_serial_port()
print('serial_port: ', serial_port)
if serial_port is None:
    print("No Pozyx connected. Check your USB cable or your driver!")
    quit()

pozyx = PozyxSerial(serial_port)
sensor_data = SensorData()

remote_id = 0x6a31
if pozyx.checkForFlag(POZYX_INT_MASK_IMU, 0.01) == POZYX_SUCCESS:
    status = pozyx.getAllSensorData(sensor_data, remote_id)
    print("sensor_data = \n", sensor_data)

remote_id = 0x6a35
if pozyx.checkForFlag(POZYX_INT_MASK_IMU, 0.01) == POZYX_SUCCESS:
    for i in range(5000):
        sleep(.5)
        status = pozyx.getAllSensorData(sensor_data, remote_id)
        print(sensor_data.euler_angles)
     

# pozyx.getAllSensorData(sensor_data, 0x6a31)
# print("sensor_data = \n", sensor_data)
# pozyx.getAllSensorData(sensor_data, 0x6a35)
# print("sensor_data = \n", sensor_data)