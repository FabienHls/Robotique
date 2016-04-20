import pygame
import time
from pygame.locals import *

TAILLE_FENETRE = 500
TAILLE_RETICULE = 100
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
pygame.display.flip()

quit = False
while not(quit): 
	for event in pygame.event.get():
	    #Leave the program
	    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
	        quit = True
	    if event.type == MOUSEMOTION:
	        #On change les coordonnees du reticule en appliquant une correction
	        x = event.pos[0] - 5
	        y = event.pos[1] - 5
	    	x_centre = TAILLE_FENETRE/2 - (TAILLE_FENETRE - x)
	    	y_centre = TAILLE_FENETRE/2 - y
	print 'position envoyee :', x_centre/2, y_centre/2
	print 'position non modifiee:', x,y
	time.sleep(0.2)
	window.blit(background, (0,0))
	window.blit(reticule,(x - TAILLE_RETICULE/2 + 5,y - TAILLE_RETICULE/2 + 4))
	pygame.display.flip()
