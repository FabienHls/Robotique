import itertools
import time
import numpy
import pypot.dynamixel

from math import *

#Function to change motors id
def changeID(old, new):
    verif = 0
    # we can scan the motors
    found_ids = dxl_io.scan()  # this may take several seconds
    print 'Detected:', found_ids

    for i in found_ids:
        if i == old:
                dxl_io.change_id({old: new})
                print "Ancien id: ", old, " Nouvel id: ", new

#Al-kashi theorem
def al_kashi(a, b, c):
    return acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b))

def leg_dk(theta1, theta2, theta3, l1=51, l2=63.7, l3=93):

    correction_theta2 = -20.69
    correction_theta3 = 90 + correction_theta2 - 5.06

    theta1 = radians(theta1)
    theta2 = radians(theta2-correction_theta2)
    theta3 = radians(-(theta3-correction_theta3))


    d12 = l2 * cos(theta2)
    d23 = l3 * cos(theta2 + theta3)

    plan_contribution = l1 + d12 + d23


    x = cos(theta1) * plan_contribution
    y = sin(theta1) * plan_contribution
    z = - (l2 * sin(theta2) +l3 * sin(theta2 + theta3))

    return (x,y,z)

def leg_ik(x, y, z, l1=51, l2=63.7, l3=93):
    # Alpha is a negative angle
    alpha = -20.69
    beta = 5.06

    # Correction of the 2 angles theta 2 and theta3 with alpha and beta
    correction_theta2 = alpha
    correction_theta3 = - 90 + correction_theta2 - beta

    theta1 = atan2(y, x)

    d13 = sqrt(y ** 2 + x ** 2) - l1
    d = sqrt(z ** 2 + d13 ** 2)

    a = atan2(z, d13)
    b = al_kashi(l2, d, l3)
    theta2 = - a - b

    theta3 = al_kashi(l2, l3, d)

    theta1 = degrees(theta1)
    theta2 = degrees(theta2) + correction_theta2
    theta3 = degrees(theta3) + correction_theta3

    return (theta1,theta2,theta3)

if __name__ == '__main__':

    # we first open the Dynamixel serial port
    with pypot.dynamixel.DxlIO('/dev/ttyUSB0', baudrate=1000000) as dxl_io:

        found_ids= dxl_io.scan()
        dxl_io.enable_torque(found_ids)

        # we get the current positions
        print 'Current pos:', dxl_io.get_present_position(found_ids)

        # we create a python dictionnary: {id0 : position0, id1 : position1...}
        pos = dict(zip(found_ids, itertools.repeat(0)))
        print 'Cmd:', pos

        # we send these new positions
        dxl_io.set_goal_position(pos)
        time.sleep(1)  # we wait for 1s

        # we get the current positions
        print 'New pos:', dxl_io.get_present_position(found_ids)
 
        #Sinusoid 
        '''for i in range (0,100000):
            time.sleep(0.01)
            t= time.time()
            pos2 = dict(zip(found_ids,itertools.repeat(10*numpy.sin(numpy.pi*t))))
            dxl_io.set_goal_position(pos2)
        '''
 
 
        while True:
            time.sleep(0.5)
            posActuelle=dxl_io.get_present_position(found_ids)
            position=leg_dk(posActuelle[0],posActuelle[1],posActuelle[2])
            print "X Y Z: ", position



        time.sleep(1)
       # we power off the motors
        dxl_io.disable_torque(found_ids)
        time.sleep(1)  # we wait for 1s