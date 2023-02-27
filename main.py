import pygame as pg
import sys
from pygame.locals import *
from Game import *

pg.init()

# Game Setup
FPS = 160
fpsClock = pg.time.Clock()
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
SCREENMODE = pg.RESIZABLE
#SCREENMODE = pg.FULLSCREEN
WINDOW = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), SCREENMODE, vsync=1)
pg.display.set_caption('Runner')

pg.font.init()
my_font = pg.font.SysFont('Arial', 10)

delta_time = 0


# The main function that controls the game
def main():
    global delta_time
    looping = True
    game = Game(WINDOW, WINDOW_WIDTH, WINDOW_HEIGHT)

    # The main game loop
    while looping:
        # Get inputs
        game.jumpKeyPRESSED = False
        game.jumpKeyRELEASED = False
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    game.jumpKeyDOWN = True
                    game.jumpKeyPRESSED = True
                elif event.key == pg.K_RIGHT:
                    game.horizontalInput += 1
                elif event.key == pg.K_LEFT:
                    game.horizontalInput -= 1
                elif event.key == pg.K_SPACE:
                    game.GenerateFromWall(game.walls[0])
                    print("regenerated")
            elif event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    game.jumpKeyDOWN = False
                    game.jumpKeyRELEASED = True
                elif event.key == pg.K_RIGHT:
                    game.horizontalInput -= 1
                elif event.key == pg.K_LEFT:
                    game.horizontalInput += 1
        game.Loop()
        pg.display.update()
        game.delta_time = fpsClock.tick(FPS) / 1000


main()
