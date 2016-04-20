import itertools
import time
import numpy
import pypot.dynamixel
import pypot.robot

from contextlib import closing
from math import *


import pygame
from pygame.locals import *


# CONSTANTES 
INIT_X = 118.79
INIT_Y = 0
INIT_Z = -90
constL1 = 51
constL2 = 63.7
constL3 = 93
TAILLE_FENETRE = 500
TAILLE_RETICULE = 100
# Angle to match the theory with reality for theta 2 (measures of the triangle are 22.5, 60.7, 63.7). => Angle =  -20.69
theta2Correction = -20.69
# Same goes for theta 3 : +90 - 20.69 - a. Where a = asin(8.2/93) = 5.06
theta3Correction = 90 + theta2Correction - 5.06

#PYGAME INITIALISATION
pygame.init()
window = pygame.display.set_mode((TAILLE_FENETRE, TAILLE_FENETRE))
background = pygame.image.load("images/grille.png").convert()
background = pygame.transform.scale(background, (TAILLE_FENETRE, TAILLE_FENETRE))
window.blit(background, (0,0))
reticule = pygame.image.load("images/plus.png").convert_alpha()
reticule = pygame.transform.scale(reticule, (TAILLE_RETICULE, TAILLE_RETICULE))
window.blit(reticule, (TAILLE_FENETRE/2 - TAILLE_RETICULE/2, TAILLE_FENETRE/2 - TAILLE_RETICULE/2))
#Rafraichissement de l'ecran
pygame.display.flip()

# Given the sizes (a, b, c) of the 3 sides of a triangle, returns the angle between a and b using the alKashi theorem.
def alKashi(a, b, c):
    value = ((a*a)+(b*b)-(c*c))/(2*a*b)
    #Note : to get the other altenative, simply change the sign of the return :
    return -acos(value)


# Computes the direct kinematics of a leg in the leg's frame
# Given the angles (theta1, theta2, theta3) of a limb with 3 rotational axes separated by the distances (l1, l2, l3),
# returns the destination point (x, y, z)
def computeDK(theta1, theta2, theta3, l1=constL1, l2=constL2,l3=constL3) :
    theta1 = theta1 * pi / 180.0
    theta2 = (theta2 - theta2Correction) * pi / 180.0
    theta3 = -(theta3 - theta3Correction) * pi / 180.0

    planContribution = l1 + l2*cos(theta2) + l3*cos(theta2 + theta3)

    x = cos(theta1) * planContribution
    y = sin(theta1) * planContribution
    z = -(l2 * sin(theta2) + l3 * sin(theta2 + theta3))

    return [x, y, z]

# Computes the inverse kinematics of a leg in the leg's frame
# Given the destination point (x, y, z) of a limb with 3 rotational axes separated by the distances (l1, l2, l3),
# returns the angles to apply to the 3 axes
def computeIK(x, y, z, l1=constL1, l2=constL2,l3=constL3) :
    # theta1 is simply the angle of the leg in the X/Y plane. We have the first angle we wanted.
    theta1 = atan2(y, x)

    # Distance between the second motor and the projection of the end of the leg on the X/Y plane
    xp = sqrt(x*x+y*y)-l1
    if (xp < 0) :
        print("Destination point too close")
        xp = 0

    # Distance between the second motor arm and the end of the leg
    d = sqrt(pow(xp,2) + pow(z,2))
    if (d > l2+l3):
        print("Destination point too far away")
        d = l2+l3

    # Knowing l2, l3 and d, theta1 and theta2 can be computed using the Al Kashi law
    theta2 = alKashi(l2, d, l3) - atan2(z, xp)
    theta3 = pi - alKashi(l2, l3, d)

    return [modulo180(degrees(theta1)), modulo180(degrees(theta2) + theta2Correction), modulo180(degrees(theta3) + theta3Correction)]

#Takes an angle that's between 0 and 360 and returns an angle that is between -180 and 180
def modulo180(angle) :
    if (-180 < angle < 180) :
        return angle

    angle  = angle % 360
    if (angle > 180) :
        return -360 + angle

    return angle


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


def envoyer_pos(x,y,z,leg):
        angles = computeIK(x,y,z)
        print "angles:", angles
        i=0
        for m in leg:
            m.goal_position = angles[i]
            i=i+1

def envoyer_angles(theta1,theta2,theta3,robot,motorName):
        positions = computeDK(theta1,theta2,theta3)
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

def move_leg(x,y,z,leg):
    envoyer_pos(x,y,z,leg)
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
    envoyer_pos(INIT_X, -45, INIT_Z, robot.leg6)
    envoyer_pos(INIT_X, 45, INIT_Z, robot.leg5)
    envoyer_pos(INIT_X, 0, INIT_Z,robot.leg4)
    envoyer_pos(INIT_X, -45, INIT_Z,robot.leg3)
    envoyer_pos(INIT_X, 45, INIT_Z,robot.leg2)
    envoyer_pos(INIT_X, 0, INIT_Z, robot.leg1)
    time.sleep(1)

    while True:
        #Descend le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.5)
        #Leve le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z + PAS_Z , robot.leg4)
        time.sleep(0.5)

        #Deplace en +y le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg4)
        time.sleep(0.5)
        #Deplace en -y le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.5)

        #Descend le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z - PAS_Z ,robot.leg4)
        time.sleep(0.5)
        #Leve le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.5)

        #Deplace en +y le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.5)
        #Deplace en -y le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z - PAS_Z , robot.leg4)
        time.sleep(0.5)

def rotate_robot():
    PAS_Z = 20
    #Placements Marche
    envoyer_pos(INIT_X, -45, INIT_Z, robot.leg6)
    envoyer_pos(INIT_X, 45, INIT_Z, robot.leg5)
    envoyer_pos(INIT_X, 0, INIT_Z,robot.leg4)
    envoyer_pos(INIT_X, -45, INIT_Z,robot.leg3)
    envoyer_pos(INIT_X, 45, INIT_Z,robot.leg2)
    envoyer_pos(INIT_X, 0, INIT_Z, robot.leg1)
    time.sleep(1)

    while True:
        #Descend le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.5)
        #Leve le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z + PAS_Z , robot.leg4)
        time.sleep(0.5)

        #Deplace en +y le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 65, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 25, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z + PAS_Z ,robot.leg4)
        time.sleep(0.5)
        #Deplace en -y le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 65, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 25, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.5)

        #Descend le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 65, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 25, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z - PAS_Z ,robot.leg4)
        time.sleep(0.5)
        #Leve le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 65, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 25, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.5)

        #Deplace en +y le groupe 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.5)
        #Deplace en -y le groupe 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z , robot.leg4)
        time.sleep(0.5)



#################################################

if __name__ == '__main__':


    with closing(pypot.robot.from_json('robotConfig.json')) as robot:

        quit = False
        # we power on the motors        
        for m in robot.motors:
            m.compliant = False #debloquer les moteurs
            print 'Detected:', robot.motors

        initilisation_pos()

        while not(quit): 
            for event in pygame.event.get():
                #Leave the program
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                    quit = True
                if event.type == MOUSEMOTION:
                    #On change les coordonnees du reticule
                    x = event.pos[0] - TAILLE_RETICULE/2
                    y = event.pos[1] - TAILLE_RETICULE/2
                    x_centre = TAILLE_FENETRE/2 - (TAILLE_FENETRE - x)
                    y_centre = TAILLE_FENETRE/2 - y
                    print 'position envoyee :', x_centre/7 + 8, y_centre/7 - 6
                    window.blit(background, (0,0))
                    window.blit(reticule,(x - TAILLE_RETICULE/2 + 5,y - TAILLE_RETICULE/2 + 4))
                    pygame.display.flip()
                    move_center(x_centre/7 + 8,y_centre/7 - 6,-10)


     
            #move_leg(100,50,-40,robot.leg1)
            #move_center(30,30,-10)
            #walk_straight_line()
            #rotate_robot()

        #for m in robot.leg1:
         #    print(m.present_position)
       
        # we power off the motors
        time.sleep(2)  # we wait for 1s
        for m in robot.motors:
            m.compliant=True #rebloquer moteurs
        time.sleep(1)  # we wait for 1s
