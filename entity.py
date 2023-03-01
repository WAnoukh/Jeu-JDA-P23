from math import ceil
from random import randint

import pygame as pg
import pygame.transform

from functions import *
from Texture import *


class Entity:
    id = 0
    sizeX = 1
    sizeY = 1
    visible = True
    solid = False
    pivotX = 0.5
    pivotY = 0.5
    color = (255, 105, 180)
    game = None

    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.game = game

    def Update(self, game):
        pass

    def Draw(self, window, camera):
        sizeX, sizeY = self.sizeX * camera.zoom, self.sizeY * camera.zoom
        offsetX = sizeX * self.pivotX
        offsetY = sizeY * self.pivotY
        x, y = camera.WorldToScreen(self.x, self.y)
        pg.draw.rect(window, self.color,
                     pg.Rect(x - offsetX, y - offsetY, sizeX, sizeY))
        self.game.printTextOnScreen(self.id, x, y)
        return x - offsetX, y - offsetY

    def GetTopLeftPoint(self):
        return self.x - self.sizeX * self.pivotX, self.y - self.sizeY * self.pivotY

    def GetCenter(self):
        return self.x - 0.5 * self.sizeX, self.y - 0.5 * self.sizeY

    def PointCollide(self, x, y):
        wx, wy = self.GetTopLeftPoint()
        return (wx < x < wx + self.sizeX) and (wy < y < wy + self.sizeY)

    def BoxCollide(self, x1, y1, x2, y2):
        sx1, sy1 = self.GetTopLeftPoint()
        sx2, sy2 = sx1 + self.sizeX, sy1 + self.sizeY
        if self.PointCollide(x1, y1) or self.PointCollide(x2, y1) or self.PointCollide(x1, y2) or \
                self.PointCollide(x2, y2):
            return True
        if sx1 <= x1 <= sx2 or sx1 <= x2 <= sx2:
            if y1 <= sy1 and sy2 <= y2:
                return True
        if sy1 <= y1 <= sy2 or sy1 <= y2 <= sy2:
            if x1 <= sx1 and sx2 <= x2:
                return True
        if y1 < sy1 and sy2 < y2 and x1 < sx1 and sx2 < x2:
            return True
        return False


class Wall(Entity):
    placed = True
    morphDuration = 2
    morphStart = 0
    startX = 0
    startY = 0
    startSizeX = 0
    startSizeY = 0
    texture = None

    def __init__(self, x, y, sizeX, sizeY, game, dx=None, dy=None, dsx=None, dsy=None):
        super().__init__(x, y, game)
        self.pivotX = 0.5
        self.pivotY = 0

        self.texture = game.wallTexture

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
            if self.sizeX != self.desiredSizeX:
                self.sizeX = SmoothLerp(self.startSizeX, self.desiredSizeX, curTime, self.morphStart, endTime)
            if self.sizeY != self.desiredSizeY:
                self.sizeY = SmoothLerp(self.startSizeY, self.desiredSizeY, curTime, self.morphStart, endTime)

    def Draw(self, window, camera):
        sizeX, sizeY = self.sizeX * camera.zoom, self.sizeY * camera.zoom
        offsetX = sizeX * self.pivotX
        offsetY = sizeY * self.pivotY
        x, y = camera.WorldToScreen(self.x, self.y)
        x, y = x - offsetX, y - offsetY
        if self.texture is not None:
            self.texture.Draw(window, x, y, self.sizeX, self.sizeY, camera)
            self.game.printTextOnScreen(self.id, x, y)
        pass

    def GetDesiredTopLeftPoint(self):
        return self.desiredX - self.desiredSizeX * self.pivotX, self.desiredY - self.desiredSizeY * self.pivotY

    def PointDesiredCollide(self, x, y):
        wx, wy = self.GetDesiredTopLeftPoint()
        return (wx < x < wx + self.sizeX) and (wy < y < wy + self.sizeY)


class Player(Entity):
    pivotX = 0.5
    pivotY = 1
    color = (200, 0, 0)
    sizeY = 12 * 2
    sizeX = 9

    xSpeed = 0
    ySpeed = 0

    jumpRequested = False

    landed = False
    lastLanded = -5000
    jumpOffset = 0.1
    jumpForce = 800
    gravity = 1800

    isWallTouching = 0  # 0 for False and 1 or -1 according to the side
    wallSlidingRate = 0.9
    lastWalled = -5000
    lastWallDir = 0
    wallJumpOffset = 0.13
    wallJumpBoost = 200

    movSpeed = 400
    movAcc = 0.2
    movDec = 0.3

    lastHorizontalInput = 1

    def __init__(self, x, y, game):
        super().__init__(x, y, game)
        animations = ConvertPlayerSpriteSheet("SpriteSheet_Player.png")
        self.idleAnim, self.runAnim, self.jumpAnim, self.fallAnim, self.slideAnim = animations

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
        elif game.jumpKeyRELEASED:
            self.jumpRequested = False

        if self.jumpRequested:
            timer = pg.time.get_ticks()
            if (timer - self.lastWalled) / 1000 < self.wallJumpOffset and not self.landed:
                self.ySpeed = -self.jumpForce
                self.xSpeed = -self.wallJumpBoost * self.lastWallDir
                self.jumpRequested = False
                self.lastWalled = -100000
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
        if yStep == 0:
            pass
            self.y = ceil(self.y)
        else:
            self.y += yStep * ySpeedDir

        while not game.place_free(self, self.x, self.y):
            self.y -= 1

        if self.game.horizontalInput != 0:
            self.lastHorizontalInput = self.game.horizontalInput

    def Draw(self, window, camera):
        animSpeed = 0.2
        # super().Draw(window, camera)
        if self.landed:
            if self.xSpeed != 0:
                curAnimation = self.runAnim
            else:
                curAnimation = self.idleAnim
                animSpeed = 1
        else:
            if self.isWallTouching == self.game.horizontalInput != 0:
                curAnimation = self.slideAnim
            else:
                if self.ySpeed < 0:
                    curAnimation = self.jumpAnim
                else:
                    curAnimation = self.fallAnim

        frame = curAnimation[floor(pg.time.get_ticks() / animSpeed / 1000) % len(curAnimation)]
        x, y = self.x, self.y
        x, y = camera.WorldToScreen(x, y)

        w, h = frame.get_size()
        w, h = w * self.game.texturePixelScale * camera.zoom, h * self.game.texturePixelScale * camera.zoom
        frame = pygame.transform.flip(frame, self.lastHorizontalInput < 0, 0)
        window.blit(pg.transform.scale(frame, (w, h)), (x - w / 2, y - h))


class CheckPoint(Entity):
    color = (0, 230, 0)
    pivotY = 1
    pivotX = 0.5

    parentWall = None
    sizeX = 15
    sizeY = 15

    def __init__(self, game):
        super().__init__(0, 0, game)

    def Start(self):
        self.Replace()

    def Replace(self):
        selectedWall = None
        maxDist = 0
        for _ in range(6):
            while True:
                newWall = self.game.walls[randint(1, len(self.game.walls) - 1)]
                if newWall is not self.parentWall:
                    break
            if Distance2(newWall.x - self.game.player.x, newWall.y - self.game.player.y) > maxDist:
                selectedWall = newWall
        self.parentWall = selectedWall

    def Update(self, game):
        if game.allPlaced:
            if self.parentWall is None:
                self.Replace()
            x, y = self.GetTopLeftPoint()
            if self.game.player.BoxCollide(x, y, self.x, self.y):
                self.Replace()
            self.x = self.parentWall.x
            self.y = self.parentWall.y
        else:
            self.parentWall = None

    def Draw(self, window, camera):
        if self.game.allPlaced:
            super().Draw(window, camera)


class Camera:
    def __init__(self, x, y, WINDOW_WIDTH, WINDOW_HEIGHT):
        self.x = x
        self.y = y
        self.zoom = 2
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT

    def WorldToScreen(self, x, y):
        return (x - self.x) * self.zoom + self.WINDOW_WIDTH / 2, (y - self.y) * self.zoom + self.WINDOW_HEIGHT / 2

    def ScreenToWorld(self, x, y):
        return (x - self.WINDOW_WIDTH / 2) / self.zoom + self.x, (y - self.WINDOW_HEIGHT / 2) / self.zoom + self.y
