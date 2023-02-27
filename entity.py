from math import ceil
import pygame as pg
from Game import *
from functions import *


class Entity:
    sizeX = 1
    sizeY = 1
    visible = True
    solid = False
    pivotX = 0.5
    pivotY = 0.5
    color = (255, 105, 180)

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def Update(self, game):
        pass

    def draw(self, window, camera):
        sizeX, sizeY = self.sizeX*camera.zoom, self.sizeY*camera.zoom
        offsetX = sizeX * self.pivotX
        offsetY = sizeY * self.pivotY
        x, y = camera.WorldToScreen(self.x , self.y )
        pg.draw.rect(window, self.color,
                     pg.Rect(x - offsetX, y- offsetY, sizeX, sizeY))

    def GetTopLeftPoint(self):
        return self.x - self.sizeX * self.pivotX, self.y - self.sizeY * self.pivotY

    def PointCollide(self, x, y):
        wx, wy = self.GetTopLeftPoint()
        return (wx < x < wx + self.sizeX) and (wy < y < wy + self.sizeY)


class Wall(Entity):
    placed = True
    morphDuration = 2
    morphStart = 0
    startX = 0
    startY = 0
    startSizeX = 0
    startSizeY = 0

    def __init__(self, x, y, sizeX, sizeY, dx=None, dy=None, dsx=None, dsy=None):
        super().__init__(x, y)
        self.pivotX = 0.5
        self.pivotY = 0
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.color = (200, 200, 200)

        self.desiredX = x if dx is None else dx
        self.desiredY = y if dy is None else dy
        self.desiredSizeX = sizeX if dsx is None else dsx
        self.desiredSizeY = sizeY if dsy is None else dsy

    def StartMorph(self, duration=None):
        self.placed = False
        if duration is not None:
            self.morphDuration = duration
        self.morphStart = pg.time.get_ticks()
        self.startX = self.x
        self.startY = self.y
        self.startSizeX = self.sizeX
        self.startSizeY = self.sizeY

    def Update(self, game):
        if not self.placed:
            curTime = pg.time.get_ticks()
            endTime = self.morphStart + self.morphDuration
            if curTime >= endTime:
                self.placed = True

            self.x = SmoothLerp(self.startX, self.desiredX, curTime, self.morphStart, endTime)
            self.y = SmoothLerp(self.startY, self.desiredY, curTime, self.morphStart, endTime)
            self.sizeX = SmoothLerp(self.startSizeX, self.desiredSizeX, curTime, self.morphStart, endTime)
            self.sizeY = SmoothLerp(self.startSizeY, self.desiredSizeY, curTime, self.morphStart, endTime)

    def GetDesiredTopLeftPoint(self):
        return self.desiredX - self.desiredSizeX * self.pivotX, self.desiredY - self.desiredSizeY * self.pivotY

    def PointDesiredCollide(self, x, y):
        wx, wy = self.GetDesiredTopLeftPoint()
        return (wx < x < wx + self.sizeX) and (wy < y < wy + self.sizeY)


class Player(Entity):
    pivotX = 0.5
    pivotY = 1
    color = (200, 0, 0)
    sizeY = 25
    sizeX = 25

    xSpeed = 0
    ySpeed = 0

    jumpRequested = False

    landed = False
    lastLanded = -5000
    jumpOffset = 0.1
    jumpForce = 1000
    gravity = 2000

    isWallTouching = 0  # 0 for False and 1 or -1 according to the side
    wallSlidingRate = 0.9
    lastWalled = -5000
    lastWallDir = 0
    wallJumpOffset = 0.15
    wallJumpBoost = 200

    movSpeed = 600
    movAcc = 0.2
    movDec = 0.3

    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def Update(self, game):
        # Landed
        self.landed = not game.place_free(self, self.x, self.y + 1)
        if self.landed:
            self.lastLanded = pg.time.get_ticks()

        # Gravity
        self.ySpeed += self.gravity * game.delta_time

        # Wall Slide
        self.isWallTouching = (not game.place_free(self, self.x + 1, self.y)) - (
            not game.place_free(self, self.x - 1, self.y))
        if self.isWallTouching != 0:
            self.lastWallDir = self.isWallTouching
            self.lastWalled = pg.time.get_ticks()
        if self.isWallTouching != 0 and game.horizontalInput == self.isWallTouching and self.ySpeed > 0:
            self.ySpeed *= self.wallSlidingRate

        # Jump
        if game.jumpKeyPRESSED:
            self.jumpRequested = True
            if (pg.time.get_ticks() - self.lastWalled) / 1000 < self.wallJumpOffset and not self.landed:
                self.ySpeed = -self.jumpForce
                self.xSpeed = -self.wallJumpBoost * self.lastWallDir
                self.jumpRequested = False
                self.lastWalled = -100000
        elif game.jumpKeyRELEASED:
            self.jumpRequested = False

        if self.jumpRequested:
            timer = pg.time.get_ticks()
            if (timer - self.lastLanded) / 1000 < self.jumpOffset:
                self.ySpeed = -self.jumpForce
                self.jumpRequested = False
                self.lastLanded = -100000
        if self.ySpeed < 0 and not game.jumpKeyDOWN:
            self.ySpeed *= pow((1 - 0.99999999), game.delta_time)

        # Movement
        self.xSpeed += game.horizontalInput * (self.movSpeed / self.movAcc) * game.delta_time
        self.xSpeed = clamp(self.xSpeed, -self.movSpeed, self.movSpeed)
        if game.horizontalInput == 0:
            self.xSpeed = Annulate(self.xSpeed, (self.movSpeed / self.movDec) * game.delta_time)

        # Player Applying speed
        pSpeedXdt = self.xSpeed * game.delta_time
        pSpeedYdt = self.ySpeed * game.delta_time
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
                elif game.place_free(self, self.x + xSpeedDir * (xStep + 1),
                                     self.y + ySpeedDir * yStep):
                    xStep += 1
                else:
                    xDone = True
                    self.xSpeed = 0

            if not yDone:
                if yStep > abs(pSpeedYdt):
                    yDone = True
                    yStep = abs(pSpeedYdt)
                elif game.place_free(self, self.x + xSpeedDir * xStep,
                                     self.y + ySpeedDir * (yStep + 1)):
                    yStep += 1
                else:
                    yDone = True
                    self.ySpeed = 0

            if xDone and yDone:
                break

        self.x += xStep * xSpeedDir
        if self.ySpeed == 0:
            self.y = ceil(self.y)
        else:
            self.y += yStep * ySpeedDir


class Camera:
    def __init__(self, x, y, WINDOW_WIDTH, WINDOW_HEIGHT):
        self.x = x
        self.y = y
        self.zoom = 0.3
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT

    def WorldToScreen(self, x, y):
        return (x - self.x)*self.zoom + self.WINDOW_WIDTH / 2, (y - self.y)*self.zoom + self.WINDOW_HEIGHT / 2

    def ScreenToWorld(self, x, y):
        return (x - self.WINDOW_WIDTH / 2 )/self.zoom + self.x , (y - self.WINDOW_HEIGHT / 2)/self.zoom + self.y
