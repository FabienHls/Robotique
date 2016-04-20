import itertools
import time
import numpy
import pypot.dynamixel

from math import *

LIMITE = 100
if __name__ == '__main__':

    # we first open the Dynamixel serial port
    with pypot.dynamixel.DxlIO('/dev/ttyUSB0', baudrate=1000000) as dxl_io:
        dxl_io.set_torque_limit({11:LIMITE})
        dxl_io.set_torque_limit({12:LIMITE})
        dxl_io.set_torque_limit({13:LIMITE})

        dxl_io.set_torque_limit({21:LIMITE})
        dxl_io.set_torque_limit({22:LIMITE})
        dxl_io.set_torque_limit({23:LIMITE})

        dxl_io.set_torque_limit({31:LIMITE})
        dxl_io.set_torque_limit({32:LIMITE})
        dxl_io.set_torque_limit({33:LIMITE})

        dxl_io.set_torque_limit({41:LIMITE})
        dxl_io.set_torque_limit({42:LIMITE})
        dxl_io.set_torque_limit({43:LIMITE})

        dxl_io.set_torque_limit({51:LIMITE})
        dxl_io.set_torque_limit({52:LIMITE})
        dxl_io.set_torque_limit({53:LIMITE})

        dxl_io.set_torque_limit({61:LIMITE})
        dxl_io.set_torque_limit({62:LIMITE})
        dxl_io.set_torque_limit({63:LIMITE})