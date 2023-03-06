import sys
import pygame as pg
import pygame.display
from pygame.locals import *
from Game import *
from Texture import *
import threading

exitEvent = threading.Event()

def GetAnimation(path, list):
    frames = []
    i = 29
    while i:
        try:
            frames.append(ConvertSprite(path + "image{:04d}.png".format(i), 2))
        except:
            list.extend(frames)
            return
        if exitEvent.is_set():
            return
        i += 1


pg.init()

# Game Setup
FPS = 165
fpsClock = pg.time.Clock()
MainScale = 2
WINDOW_WIDTH = 1380 // MainScale
WINDOW_HEIGHT = 1024 // MainScale
SCREENMODE = pg.RESIZABLE
#SCREENMODE = pg.FULLSCREEN
WINDOW = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), SCREENMODE, vsync=0)
pg.display.set_caption('Runner')

pg.font.init()
fontDebug = pg.font.SysFont('Arial', 10)

delta_time = 0

curentFrame = 0
lastFrameTime = 0



# The main function that controls the game
def main():
    global delta_time
    looping = True
    textureScale = MainScale
    game = Game(WINDOW, WINDOW_WIDTH, WINDOW_HEIGHT, textureScale)
    game.fontDebug = fontDebug
    Anim = []
    # Anim = GetAnimation(game.execPath + "\Animation\\")

    thread = threading.Thread(target=GetAnimation, args=(game.execPath + "\Animation\\", Anim))
    thread.start()
    w, h = game.fontScore.size("Loading...")
    texts = ["Loading...", "Loading..", "Loading.", "Loading"]
    while thread.is_alive():
        i = -pg.time.get_ticks() / 1000 * 3
        WINDOW.fill((0, 0, 0))
        game.printTextOnScreen(texts[int(i) % len(texts)], WINDOW_WIDTH - w - 30,
                               WINDOW_HEIGHT - h - 30, game.fontScore)
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE or event.key == pg.K_KP_ENTER or event.key == pg.K_RETURN or event.key == pg.K_BACKSPACE:
                    pg.quit()
                    sys.exit()
                else:
                    exitEvent.set()
            if event.type == QUIT:
                pg.quit()
                sys.exit()
        pg.display.update()
        fpsClock.tick()

    thread.join()

    animStart = pg.time.get_ticks()
    playing = True
    while playing:
        i = int((pg.time.get_ticks() - animStart) / 1000 * 25)
        if i >= len(Anim):
            break
        WINDOW.blit(Anim[i], (0, 0))

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE or event.key == pg.K_KP_ENTER or event.key == pg.K_RETURN or event.key == pg.K_BACKSPACE:
                    pg.quit()
                    sys.exit()
                else:
                    playing = False
            if event.type == QUIT:
                pg.quit()
                sys.exit()

        pg.display.update()
        fpsClock.tick()
    Anim = []

    # The main game loop
    while looping:
        # Get inputs
        game.jumpKeyPRESSED = False
        game.jumpKeyRELEASED = False
        game.horizontalKeyPressed = False
        game.verticalKeyPressed = False
        game.greenPressed = False
        game.bluePressed = False
        game.purplePressed = False
        for event in pg.event.get():

            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_KP1 or event.key == pg.K_w:
                    game.jumpKeyDOWN = True
                    game.jumpKeyPRESSED = True
                if event.key == pg.K_KP4 or event.key == pg.K_v:
                    game.greenPressed = True
                if event.key == pg.K_KP5 or event.key == pg.K_b:
                    game.bluePressed = True
                if event.key == pg.K_KP6 or event.key == pg.K_n:
                    game.purplePressed = True
                elif event.key == pg.K_UP or event.key == pg.K_z:
                    game.verticalInput += 1
                    game.verticalKeyPressed = True
                elif event.key == pg.K_DOWN or event.key == pg.K_s:
                    game.verticalInput -= 1
                    game.verticalKeyPressed = True
                elif event.key == pg.K_RIGHT or event.key == pg.K_d:
                    game.horizontalInput += 1
                    game.horizontalKeyPressed = True
                elif event.key == pg.K_LEFT or event.key == pg.K_q:
                    game.horizontalInput -= 1
                    game.horizontalKeyPressed = True
                elif event.key == pg.K_SPACE:
                    game.GenerateFromWall(game.walls[0])
                elif event.key == pg.K_r:
                    game.Start()
                elif event.key == pg.K_ESCAPE or event.key == pg.K_KP_ENTER or event.key == pg.K_RETURN or event.key == pg.K_BACKSPACE:
                    pg.quit()
                    sys.exit()
            elif event.type == pg.KEYUP:
                if event.key == pg.K_KP1 or event.key == pg.K_w:
                    game.jumpKeyDOWN = False
                    game.jumpKeyRELEASED = True
                elif event.key == pg.K_RIGHT or event.key == pg.K_d:
                    game.horizontalInput -= 1
                elif event.key == pg.K_LEFT or event.key == pg.K_q:
                    game.horizontalInput += 1
                elif event.key == pg.K_UP or event.key == pg.K_z:
                    game.verticalInput -= 1
                elif event.key == pg.K_DOWN or event.key == pg.K_s:
                    game.verticalInput += 1
        game.verticalInput = clamp(game.verticalInput, -1, 1)
        game.Loop()
        pg.display.update()
        game.delta_time = fpsClock.tick(FPS) / 1000


if __name__ == '__main__':
    main()
