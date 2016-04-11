import itertools
import time
import numpy
import pypot.dynamixel
import pypot.robot

from contextlib import closing
from math import *

INIT_X = 118.79
INIT_Y = 0
INIT_Z = -90

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
    if (d13 < 0) :
        print("Destination point too close, max position sent")
        d13 = 0

    d = sqrt(z ** 2 + d13 ** 2)
    if (d > l2+l3):
        print("Destination point too far away, max position sent")
        d = l2+l3

    a = atan2(z, d13)
    b = al_kashi(l2, d, l3)
    theta2 = - a - b

    theta3 = al_kashi(l2, l3, d)

    theta1 = degrees(theta1)
    theta2 = degrees(theta2) + correction_theta2
    theta3 = degrees(theta3) + correction_theta3

    return (theta1,theta2,theta3)

def envoyer_pos(x,y,z,leg):
        angles = leg_ik(x,y,z)
        print "angles:", angles
        i=0
        for m in leg:
            m.goal_position = angles[i]
            i=i+1

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

def initilisation_pos():
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg6)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg5)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z,robot.leg4)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z,robot.leg3)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z,robot.leg2)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg1)
    time.sleep(1)

def move_center(x,y,z):

    envoyer_pos(INIT_X, -x+y + INIT_Y, INIT_Z+z, robot.leg1)
    envoyer_pos(INIT_X, x+y + INIT_Y, INIT_Z+z,robot.leg4)
    if y < 0:
        envoyer_pos(INIT_X+x, y + INIT_Y , INIT_Z+z,robot.leg2)
        envoyer_pos(INIT_X-x, -y + INIT_Y, INIT_Z+z, robot.leg6)
        envoyer_pos(INIT_X-x, -y + INIT_Y, INIT_Z+z, robot.leg5)
        envoyer_pos(INIT_X+x, y + INIT_Y, INIT_Z+z,robot.leg3)

    else:
        envoyer_pos(INIT_X-x, -y + INIT_Y, INIT_Z+z, robot.leg5)
        envoyer_pos(INIT_X+x, y + INIT_Y, INIT_Z+z,robot.leg3)
        envoyer_pos(INIT_X+x, y + INIT_Y, INIT_Z+z,robot.leg2)
        envoyer_pos(INIT_X-x, -y + INIT_Y, INIT_Z+z, robot.leg6)

def walk_straight_line():
    PAS_Z = 20
    #Placements Marche
    envoyer_pos(INIT_X, -20, INIT_Z, robot.leg6)
    envoyer_pos(INIT_X, 20, INIT_Z, robot.leg5)
    envoyer_pos(INIT_X, 0, INIT_Z,robot.leg4)
    envoyer_pos(INIT_X, -20, INIT_Z,robot.leg3)
    envoyer_pos(INIT_X, 20, INIT_Z,robot.leg2)
    envoyer_pos(INIT_X, 0, INIT_Z, robot.leg1)
    time.sleep(1)

    while True:
        #Leve le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 20, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z + PAS_Z , robot.leg4)
        #Descend le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 20, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.5)

        #Deplace en +y le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 40, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 40, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg4)
        #Deplace en -y le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 40, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 40, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.15)

        #Descend le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 40, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 40, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z ,robot.leg4)
        #Leve le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 40, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 40, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.5)

        #Deplace en -y le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 20, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z - PAS_Z , robot.leg4)
        #Deplace en +y le groupe 135
        envoyer_pos(INIT_X, INIT_Y - 40, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y + 40, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.5)





#################################################

if __name__ == '__main__':


    with closing(pypot.robot.from_json('robotConfig.json')) as robot:

        # we power on the motors
        
        for m in robot.motors:
            m.compliant = False #debloquer les moteurs
            print 'Detected:', robot.motors

        initilisation_pos()

        time.sleep(1)
        '''while True:
            t=time.time()
            for i in range(1,7):
                envoyer_pos(INIT_X, 0, INIT_Z+10*sin(2*pi*t*2),robot,"motor_"+str(i))'''

 
        #move_center(30,30,-10)
        walk_straight_line()

        #for m in robot.leg1:
         #    print(m.present_position)
       
        # we power off the motors
        time.sleep(2)  # we wait for 1s
        for m in robot.motors:
            m.compliant=True #rebloquer moteurs
        time.sleep(1)  # we wait for 1s
