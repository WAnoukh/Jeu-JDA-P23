import pygame
import pygame as pg
import sys
from functions import *
from entity import *
from pygame.locals import *

pg.init()

# Colours
BACKGROUND = (255, 255, 255)

# Game Setup
FPS = 165
fpsClock = pg.time.Clock()
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900

WINDOW = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption('Runner')

delta_time = 0


class Game:
    def __init__(self, window):
        self.WINDOW = window

        self.player = Player(0, -0)
        self.pSpeedX = 0
        self.pSpeedY = 0

        self.pLanded = False
        self.pLastLanded = -5000
        self.pJumpOffset = 0.1
        self.jumpRequested = False
        self.pJumpForce = 1000
        self.gravity = 2000

        self.pMovSpeed = 400
        self.pMovAcc = 0.2
        self.pMovDec = 0.3

        self.walls = [Wall(0, 0, 500, 200)]

        self.MainCamera = Camera(self.player.x, self.player.y, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.camDesiredX = self.player.x
        self.camDesiredY = self.player.y

    def Update(self):

        # Landed
        self.pLanded = not self.place_free(self.player, self.player.x, self.player.y + 1)
        if self.pLanded:
            self.pLastLanded = pg.time.get_ticks()

        # Gravity
        self.pSpeedY += self.gravity * delta_time

        # Jump
        if jumpKeyPRESSED:
            self.jumpRequested = True
        # elif jumpKeyDOWN :
        #    self.jumpRequested = False
        if self.jumpRequested:
            timer = pg.time.get_ticks()
            if (timer - self.pLastLanded) / 1000 < self.pJumpOffset and self.jumpRequested:
                self.pSpeedY = -self.pJumpForce
                self.jumpRequested = False
                self.pLastLanded = -100000
        if self.pSpeedY < 0 and not jumpKeyDOWN:
            self.pSpeedY *= pow((1 - 0.99999999), delta_time)

        # Movement
        self.pSpeedX += horizontalInput * (self.pMovSpeed / self.pMovAcc) * delta_time
        self.pSpeedX = clamp(self.pSpeedX, -self.pMovSpeed, self.pMovSpeed)
        if horizontalInput == 0:
            self.pSpeedX = Annulate(self.pSpeedX, (self.pMovSpeed / self.pMovDec) * delta_time)
        else:
            pass
        # Player Applying speed
        pSpeedXdt = self.pSpeedX * delta_time
        pSpeedYdt = self.pSpeedY * delta_time
        xSpeedDir = sign(pSpeedXdt)
        ySpeedDir = sign(pSpeedYdt)
        xDone = False
        yDone = False

        xStep = 0
        yStep = 0
        while True:

            if not xDone:
                if xStep > abs(pSpeedXdt):
                    xDone = True
                    xStep = abs(pSpeedXdt)
                elif self.place_free(self.player, self.player.x + xSpeedDir * (xStep + 1),
                                     self.player.y + ySpeedDir * yStep):
                    xStep += 1
                else:
                    xDone = True
                    self.pSpeedX = 0

            if not yDone:
                if yStep > abs(pSpeedYdt):
                    yDone = True
                    yStep = abs(pSpeedYdt)
                elif self.place_free(self.player, self.player.x + xSpeedDir * xStep,
                                     self.player.y + ySpeedDir * (yStep + 1)):
                    yStep += 1
                else:
                    yDone = True
                    self.pSpeedY = 0

            if xDone and yDone:
                break

        self.player.x += xStep * xSpeedDir
        self.player.y += yStep * ySpeedDir

        # camera
        self.camDesiredX = lerpDt(self.camDesiredX, self.player.x, 0.9, delta_time)
        self.camDesiredY = lerpDt(self.camDesiredY, self.player.y, 0.9, delta_time)
        self.MainCamera.x = round(self.camDesiredX)
        self.MainCamera.y = round(self.camDesiredY)

    def Draw(self):
        self.WINDOW.fill(BACKGROUND)
        for wall in self.walls:
            wall.draw(self.WINDOW, self.MainCamera)
        self.player.draw(self.WINDOW, self.MainCamera)

        x, y = pg.mouse.get_pos()
        wx, wy = self.MainCamera.ScreenToWorld(x, y)
        place = self.place_free(self.player, wx, wy)
        pg.draw.rect(self.WINDOW, (255 * place, 255 * (not place), 0), Rect(x, y, 10, 10))

    def place_free(self, entity, x, y):
        x -= entity.pivotX * entity.sizeX
        y -= entity.pivotY * entity.sizeY
        for wall in self.walls:
            wx, wy = wall.GetTopLeftPoint()

            def inWall(a, b):
                return (wx < a <= wx + wall.sizeX) and (wy < b <= wy + wall.sizeY)

            if inWall(x, y) or inWall(x + entity.sizeX, y) or inWall(x, y + entity.sizeY) or inWall(x + entity.sizeY,
                                                                                                    y + entity.sizeY):
                return False

        return True

    def Loop(self):
        self.Update()
        self.Draw()


jumpKeyDOWN = False
jumpKeyPRESSED = False
jumpKeyRELEASED = False

horizontalInput = 0


# The main function that controls the game
def main():
    global delta_time, jumpKeyDOWN, jumpKeyPRESSED, jumpKeyRELEASED, horizontalInput
    looping = True
    game = Game(WINDOW)

    # The main game loop
    while looping:
        # Get inputs
        jumpKeyPRESSED = False
        jumpKeyRELEASED = True
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    jumpKeyDOWN = True
                    jumpKeyPRESSED = True
                elif event.key == pygame.K_RIGHT:
                    horizontalInput += 1
                elif event.key == pygame.K_LEFT:
                    horizontalInput -= 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    jumpKeyDOWN = False
                elif event.key == pygame.K_RIGHT:
                    horizontalInput -= 1
                elif event.key == pygame.K_LEFT:
                    horizontalInput += 1
        game.Loop()

        pg.display.update()
        delta_time = fpsClock.tick(FPS) / 1000


main()
