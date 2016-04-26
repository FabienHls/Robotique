import pygame
import time
from pygame.locals import *

TAILLE_FENETRE = 500
TAILLE_RETICULE = 100
LONGUEUR_RECT_BLANC = 400
HAUTEUR_RECT_BLANC = 30
x=0
y=0
x_centre=0
y_centre=0


#PYGAME INITIALISATION
pygame.init()
window = pygame.display.set_mode((TAILLE_FENETRE, TAILLE_FENETRE))
background = pygame.image.load("images/grille.png").convert()
background = pygame.transform.scale(background, (TAILLE_FENETRE, TAILLE_FENETRE))
window.blit(background, (0,0))

reticule = pygame.image.load("images/plus.png").convert_alpha()
reticule = pygame.transform.scale(reticule, (TAILLE_RETICULE, TAILLE_RETICULE))
window.blit(reticule, (TAILLE_FENETRE/2 - TAILLE_RETICULE/2, TAILLE_FENETRE/2 - TAILLE_RETICULE/2))

rect_blanc = pygame.image.load("images/rect_blanc.jpg").convert_alpha()
rect_blanc = pygame.transform.scale(rect_blanc, (LONGUEUR_RECT_BLANC, HAUTEUR_RECT_BLANC))
background.blit(rect_blanc,(10,10))
if pygame.font:
	font = pygame.font.Font(None, 36)
	text = font.render("Mode:", 1, pygame.Color("red"))
	textpos = text.get_rect()
	textpos.center = 50,20
	background.blit(text, textpos)
pygame.display.flip()
	
quit = False
leg = False
center = False
walk_line = False
rotate = False
while not(quit): 
	for event in pygame.event.get():
	    #Leave the program
	    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
	        quit = True
	        background.blit(rect_blanc,(10,10))
	        text = font.render("En fermeture ...", 1, pygame.Color("red"))
            background.blit(text, textpos)
        if (event.type == KEYDOWN and event.key == K_l):
            leg = True
            background.blit(rect_blanc,(10,10))
            text = font.render("Mode: Leg", 1, pygame.Color("red"))
            background.blit(text, textpos)
        if (event.type == KEYDOWN and event.key == K_c):
            center = True
            background.blit(rect_blanc,(10,10))
            text = font.render("Mode: Move center", 1, pygame.Color("red"))
            background.blit(text, textpos)
        if (event.type == KEYDOWN and event.key == K_w):
            walk_line = True
            background.blit(rect_blanc,(10,10))
            text = font.render("Mode: Walk straight line", 1, pygame.Color("red"))
            background.blit(text, textpos)
            pygame.display.update()
        if (event.type == KEYDOWN and event.key == K_r):
            rotate = True
            background.blit(rect_blanc,(10,10))
            text = font.render("Mode: Rotate center", 1, pygame.Color("red"))
            background.blit(text, textpos)
            pygame.display.update()
	    if event.type == MOUSEMOTION:
	        #On change les coordonnees du reticule en appliquant une correction
	        x = event.pos[0] - 5
	        y = event.pos[1] - 5
	    	x_centre = TAILLE_FENETRE/2 - (TAILLE_FENETRE - x)
	    	y_centre = TAILLE_FENETRE/2 - y
	print 'position envoyee :', x_centre/2, y_centre/2
	print 'position non modifiee:', x,y
	time.sleep(0.02)
	window.blit(background, (0,0))
	window.blit(reticule,(x - TAILLE_RETICULE/2 + 5,y - TAILLE_RETICULE/2 + 4))
	pygame.display.flip()
