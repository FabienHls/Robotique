import itertools
import time
import numpy
import pypot.dynamixel
import pypot.robot

from contextlib import closing
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

def envoyer_pos(x,y,z,leg):
        angles= leg_ik(x,y,z)
        print "angles:", angles
        i=0
        for m in leg:
            m.goal_position = angles[i]
            i=i+1
        '''robot.goto_position(
            {motorName+"1":angles[0],motorName+"2":angles[1],motorName+"3":angles[2]},
            0)'''

def envoyer_pos2(x,y,z,robot,motorName):
        angles= leg_ik(x,y,z)
        print "angles:", angles
        robot.goto_position(
            {motorName+"1":angles[0],motorName+"2":angles[1],motorName+"3":angles[2]},
            0)

def envoyer_angles(theta1,theta2,theta3,robot,motorName):
        positions = leg_dk(theta1,theta2,theta3)
        print "positions:",positions
        print "angles", theta1,theta2,theta3
        robot.goto_position(
            {motorName+"1":theta1,motorName+"2":theta2,motorName+"3":theta3},
            0)


def recup_pos(found_ids):
    return dxl_io.get_present_position(found_ids)

#################################################

if __name__ == '__main__':


    with closing(pypot.robot.from_json('robotConfig.json')) as robot:

        # we power on the motors
        
        for m in robot.motors:
            m.compliant = False #debloquer les moteurs
            print 'Detected:', robot.motors

        for i in range(1,7):
            time.sleep(0.5)
            envoyer_pos2(118.79, 0, -115.14,robot,"motor_"+str(i))

        time.sleep(2)
        '''while True:
            t=time.time()
            for i in range(1,7):
                envoyer_pos(118.79, 0, -115.14+10*sin(2*pi*t*2),robot,"motor_"+str(i))'''

#Placements
        '''envoyer_angles(0, -10, -30,robot,"motor_1")
        time.sleep(2)
        envoyer_angles(40, 0, 0,robot,"motor_2")
        time.sleep(2)
        envoyer_angles(10, 0, 0,robot,"motor_3")
        time.sleep(2)
        envoyer_angles(0, 10, 30,robot,"motor_4")
        time.sleep(2)
        envoyer_angles(40, 0, 0,robot,"motor_5")
        time.sleep(2)
        envoyer_angles(10, 0, 0,robot,"motor_6")
        time.sleep(2)'''

        #Axe X
        '''while True:
            envoyer_pos(85, 0, -115.14, robot, "motor_1")
            envoyer_pos(118.79, -20, -115.14, robot, "motor_3")
            envoyer_pos(118.79, -20, -115.14, robot, "motor_2")
            envoyer_pos(152.58, 0, -115.14, robot, "motor_4")
            envoyer_pos(118.79, 20, -115.14, robot, "motor_5")
            envoyer_pos(118.79, 20, -115.14, robot, "motor_6")

            time.sleep(1)
            envoyer_pos(152.58, 0, -115.14, robot, "motor_1")
            envoyer_pos(118.79, 20, -115.14, robot, "motor_3")
            envoyer_pos(118.79, 20, -115.14, robot, "motor_2")
            envoyer_pos(85, 0, -115.14, robot, "motor_4")
            envoyer_pos(118.79, -20, -115.14, robot, "motor_5")
            envoyer_pos(118.79, -20, -115.14, robot, "motor_6")
            time.sleep(1)'''

        '''while True:
                    envoyer_pos(118.79, -20, -115.14, robot, "motor_1")
                    envoyer_pos(85, 0, -115.14, robot, "motor_2")
                    envoyer_pos(85, 0, -115.14, robot, "motor_3")
                    envoyer_pos(118.79, 20, -115.14, robot, "motor_4")
                    envoyer_pos(152.58, 0, -115.14, robot, "motor_5")
                    envoyer_pos(152.58, 0, -115.14, robot, "motor_6")

                    time.sleep(1)
                    envoyer_pos(118.79, 20, -115.14, robot, "motor_1")
                    envoyer_pos(152.58, 0, -115.14, robot, "motor_2")
                    envoyer_pos(152.58, 0, -115.14, robot, "motor_3")
                    envoyer_pos(118.79, -20, -115.14, robot, "motor_4")
                    envoyer_pos(85, 0, -115.14, robot, "motor_5")
                    envoyer_pos(85, 0, -115.14, robot, "motor_6")
                    time.sleep(1)'''


        while True: 
                    envoyer_pos(152.58, 0, -115.14, robot.leg6)
                    envoyer_pos(152.58, 0, -115.14, robot.leg5)
                    envoyer_pos(118.79, 20, -115.14,robot.leg4)
                    envoyer_pos(85, 0, -115.14,robot.leg3)
                    envoyer_pos(85, 0, -115.14,robot.leg2)
                    envoyer_pos(118.79, -20, -115.14, robot.leg1)

                    time.sleep(1)
                    envoyer_pos(85, 0, -115.14, robot.leg6)
                    envoyer_pos(85, 0, -115.14, robot.leg5)
                    envoyer_pos(118.79, -20, -115.14, robot.leg4)
                    envoyer_pos(152.58, 0, -115.14, robot.leg3)
                    envoyer_pos(152.58, 0, -115.14, robot.leg2)
                    envoyer_pos(118.79, 20, -115.14, robot.leg1)                    
                    time.sleep(1)






      
        # we power off the motors
        time.sleep(30)  # we wait for 1s
        for m in robot.motors:
            m.compliant=True #rebloquer moteurs
        time.sleep(1)  # we wait for 1s
