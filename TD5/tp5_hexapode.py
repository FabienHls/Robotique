import itertools
import time
import numpy
import pypot.dynamixel
import pypot.robot

from contextlib import closing
from math import *

import pygame
from pygame.locals import *


# CONSTANTS 
INIT_X = 118.79
INIT_Y = 0
INIT_Z = -90
constL1 = 51
constL2 = 63.7
constL3 = 93
TAILLE_FENETRE = 500
TAILLE_RETICULE = 100
LONGUEUR_RECT_BLANC = 400
HAUTEUR_RECT_BLANC = 30
x_centre=0
y_centre=0
x=0
y=0


# Angle to match the theory with reality for theta 2 (measures of the triangle are 22.5, 60.7, 63.7). => Angle =  -20.69
theta2Correction = -20.69

# Same goes for theta 3 : +90 - 20.69 - a. Where a = asin(8.2/93) = 5.06
theta3Correction = 90 + theta2Correction - 5.06

#PYGAME INITIALISATION
pygame.init()
window = pygame.display.set_mode((TAILLE_FENETRE, TAILLE_FENETRE))
background = pygame.image.load("images/grille.png").convert()
background = pygame.transform.scale(background, (TAILLE_FENETRE, TAILLE_FENETRE))

#Displaying background
window.blit(background, (0,0))

reticule = pygame.image.load("images/plus.png").convert_alpha()
reticule = pygame.transform.scale(reticule, (TAILLE_RETICULE, TAILLE_RETICULE))

#Displaying reticle
window.blit(reticule, (TAILLE_FENETRE/2 - TAILLE_RETICULE/2, TAILLE_FENETRE/2 - TAILLE_RETICULE/2))

rect_blanc = pygame.image.load("images/rect_blanc.jpg").convert_alpha()
rect_blanc = pygame.transform.scale(rect_blanc, (LONGUEUR_RECT_BLANC, HAUTEUR_RECT_BLANC))

#Displaying rectangle
background.blit(rect_blanc,(10,10))

#Displaying text ont the top of the screen
if pygame.font:
    font = pygame.font.Font(None, 36)
    text = font.render("Mode:", 1, pygame.Color("red"))
    textpos = text.get_rect()
    textpos.center = 50,20
    background.blit(text, textpos)

#Screen refresh
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


#Gives a position to each motor of a given leg
#Use of ik solution
def envoyer_pos(x,y,z,leg):
        angles = computeIK(x,y,z)
        print "angles:", angles
        i=0
        for m in leg:
            m.goal_position = angles[i]
            i=i+1

#Init the position of the robot with constants
def initilisation_pos():
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg6)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg5)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg4)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg3)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg2)
    envoyer_pos(INIT_X, INIT_Y, INIT_Z, robot.leg1)
    time.sleep(1)


#Moves the leg in parameter with envoyer_pos function
def move_leg(x,y,z,leg):
    envoyer_pos(x,y,z,leg)
    time.sleep(0.02)

#Moves the center of the robot (the 6 legs are staying on the floor)
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


#Moves the robot in straight line walking
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
    start = True

    #Until we press a key the robot moves
    while start:
        #Goes down 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.2)
        #Goes up 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z + PAS_Z , robot.leg4)
        time.sleep(0.2)

        #Moves on y axe 246
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg4)
        time.sleep(0.2)
        #Moves on y axe 135
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.2)

        #Goes down 246
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X - 20, INIT_Y, INIT_Z - PAS_Z ,robot.leg4)
        time.sleep(0.2)
        #Goes up 135
        envoyer_pos(INIT_X, INIT_Y + 75, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 75, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.2)

        #Moves on y axe 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.2)
        #Moves on y axe 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X + 20, INIT_Y, INIT_Z - PAS_Z , robot.leg4)
        time.sleep(0.2)
        #If we press a key we stop
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                start = False

#Rotates without moving the center of the robot
def rotate_robot():
    PAS_Z = 20
    #Placement Marche
    envoyer_pos(INIT_X, -45, INIT_Z, robot.leg6)
    envoyer_pos(INIT_X, 45, INIT_Z, robot.leg5)
    envoyer_pos(INIT_X, 0, INIT_Z,robot.leg4)
    envoyer_pos(INIT_X, -45, INIT_Z,robot.leg3)
    envoyer_pos(INIT_X, 45, INIT_Z,robot.leg2)
    envoyer_pos(INIT_X, 0, INIT_Z, robot.leg1)
    time.sleep(1)

    start = True

    #Until we press a key the robot rotates
    while start:
        #Goes down 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.2)
        #Goes up 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z + PAS_Z , robot.leg4)
        time.sleep(0.2)

        #Moves on y axe 246
        envoyer_pos(INIT_X, INIT_Y - 65, INIT_Z + PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 25, INIT_Z + PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z + PAS_Z ,robot.leg4)
        time.sleep(0.2)
        #Moves on y axe 135
        envoyer_pos(INIT_X, INIT_Y + 65, INIT_Z - PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 25, INIT_Z - PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z - PAS_Z ,robot.leg1)
        time.sleep(0.2)

        #Goes down 246
        envoyer_pos(INIT_X, INIT_Y - 65, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 25, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z - PAS_Z ,robot.leg4)
        time.sleep(0.2)
        #Goes up 135
        envoyer_pos(INIT_X, INIT_Y + 65, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 25, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y - 20, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.2)

        #Moves on y axe 135
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z + PAS_Z , robot.leg5)
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z + PAS_Z , robot.leg3)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z + PAS_Z ,robot.leg1)
        time.sleep(0.2)#
        #Moves on y axe 246
        envoyer_pos(INIT_X, INIT_Y - 45, INIT_Z - PAS_Z , robot.leg6)
        envoyer_pos(INIT_X, INIT_Y + 45, INIT_Z - PAS_Z , robot.leg2)
        envoyer_pos(INIT_X, INIT_Y, INIT_Z - PAS_Z , robot.leg4)
        time.sleep(0.2)
        #If we press a key we stop
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                start = False



#################################################

if __name__ == '__main__':


    with closing(pypot.robot.from_json('robotConfig.json')) as robot:

        quit = False
        leg = False
        center = False
        walk_line = False
        rotate = False
        # we power on the motors        
        for m in robot.motors:
            m.compliant = False
            print 'Detected:', robot.motors

        #Init robot position
        initilisation_pos()

        while not(quit): 
            #Catch all the pygame events
            for event in pygame.event.get():

                #Leave the program
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                    quit = True
                    leg = center = walk_line = rotate = False
                    background.blit(rect_blanc,(10,10))
                    text = font.render("En fermeture ...", 1, pygame.Color("red"))
                    background.blit(text, textpos)
                    window.blit(reticule, (TAILLE_FENETRE/2 - TAILLE_RETICULE/2, TAILLE_FENETRE/2 - TAILLE_RETICULE/2))
                    initilisation_pos()
                    x=y=0
                    x_centre=y_centre=0

                #If we press a key
                if event.type == KEYDOWN:
                    #Key l
                    if event.key == K_l:
                        leg = True
                        center = walk_line = rotate = False
                        text = font.render("Mode: Leg", 1, pygame.Color("red"))

                    #Key c
                    if event.key == K_c:
                        center = True
                        leg = walk_line = rotate = False
                        text = font.render("Mode: Move center", 1, pygame.Color("red"))

                    #Key w
                    if event.key == K_w:
                        walk_line = True
                        leg = center = rotate = False
                        text = font.render("Mode: Walk straight line", 1, pygame.Color("red"))

                    #Key r
                    if event.key == K_r:
                        rotate = True
                        leg = center = walk_line = False
                        text = font.render("Mode: Rotate center", 1, pygame.Color("red"))

                    #Screen refresh and reset robot position
                    background.blit(rect_blanc,(10,10))
                    background.blit(text, textpos)
                    window.blit(reticule, (TAILLE_FENETRE/2 - TAILLE_RETICULE/2, TAILLE_FENETRE/2 - TAILLE_RETICULE/2))
                    initilisation_pos()
                    x=y=0
                    x_centre=y_centre=0

                #Use of the mouse
                if event.type == MOUSEMOTION:
                    #Change x and y of the reticle with a fix
                    x = event.pos[0] - 5
                    y = event.pos[1] - 5
                    x_centre = TAILLE_FENETRE/2 - (TAILLE_FENETRE - x)
                    y_centre = TAILLE_FENETRE/2 - y

            print 'position envoyee :', x_centre/2, y_centre/2
            print 'position non modifiee:', x,y

            time.sleep(0.02) #Between each movement

            window.blit(background, (0,0))
            window.blit(reticule,(x - TAILLE_RETICULE/2 + 5,y - TAILLE_RETICULE/2 + 4))
            pygame.display.flip()

            #Swicth case on modes
            if leg:
                move_leg(x_centre,y_centre,-40,robot.leg1)
            if center:
                move_center(x_centre/2, y_centre/2,-10)
            if walk_line:
                walk_straight_line()
                walk_line = False
            if rotate:
                rotate_robot()
                rotate = False
       
        # we power off the motors
        time.sleep(1)  # we wait for 1s
        for m in robot.motors:
            m.compliant=True 
        time.sleep(1)  # we wait for 1s
