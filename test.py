import sys
import pygame as pg
from pygame.locals import *


pg.init()

# Game Setup
FPS = 165
fpsClock = pg.time.Clock()

WINDOW_WIDTH = 200
WINDOW_HEIGHT = 200
SCREENMODE = pg.RESIZABLE
SCREENMODE = pg.FULLSCREEN
WINDOW = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), SCREENMODE, vsync=0)
pg.display.set_caption('Runner')

def main():
    looping = True
    # The main game loop
    while looping:
        for event in pg.event.get():

            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                print(str(event.key) + " is pushed")
            elif event.type == pg.KEYUP:
                print(str(event.key) + " is REALEASED")

        fpsClock.tick(FPS)


main()