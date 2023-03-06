from math import ceil, sin
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
        self.sizeX //= game.texturePixelScale
        self.sizeY //= game.texturePixelScale

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
        x, y = self.GetTopLeftPoint()
        return x + 0.5 * self.sizeX, y + 0.5 * self.sizeY

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

    isLinkedToPlayer = False
    playerRelativeX = 0
    playerRelativeY = 0

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

            if self.isLinkedToPlayer:
                game.player.x = self.x + self.playerRelativeX
                game.player.y = self.y + self.playerRelativeY

            if self.sizeX != self.desiredSizeX:
                self.sizeX = SmoothLerp(self.startSizeX, self.desiredSizeX, curTime, self.morphStart, endTime)
            if self.sizeY != self.desiredSizeY:
                self.sizeY = SmoothLerp(self.startSizeY, self.desiredSizeY, curTime, self.morphStart, endTime)
        else:
            pass
            # self.isLinkedToPlayer = False

    def Draw(self, window, camera):
        if self.game.debug:
            super().Draw(window, camera)
        sizeX, sizeY = self.sizeX * camera.zoom, self.sizeY * camera.zoom
        offsetX = sizeX * self.pivotX
        offsetY = sizeY * self.pivotY
        x, y = camera.WorldToScreen(self.x, self.y)
        x, y = x - offsetX, y - offsetY
        if self.texture is not None:
            self.texture.Draw(window, x, y, self.sizeX, self.sizeY)
        pass

    def GetDesiredTopLeftPoint(self):
        return self.desiredX - self.desiredSizeX * self.pivotX, self.desiredY - self.desiredSizeY * self.pivotY

    def PointDesiredCollide(self, x, y):
        wx, wy = self.GetDesiredTopLeftPoint()
        return (wx < x < wx + self.sizeX) and (wy < y < wy + self.sizeY)


class DecorativeWAll(Entity):
    texture = None

    def __init__(self, game):
        self.texture = game.decorativeWallTexture
        self.x = randint(0, game.WINDOW_WIDTH)
        self.y = randint(0, game.WINDOW_HEIGHT)
        w, h = randint(1, 4), randint(1, 10)
        super().__init__(self.x, self.y, game)
        self.sizeX, self.sizeY = self.texture.GetSize(w, h)

    def Update(self, game):
        self.x += 50 * game.delta_time

    def Draw(self, window, camera):
        if self.game.debug:
            super().Draw(window, camera)
        sizeX, sizeY = self.sizeX * camera.zoom, self.sizeY * camera.zoom
        offsetX = sizeX * self.pivotX
        offsetY = sizeY * self.pivotY
        x, y = self.x - offsetX, self.y - offsetY
        if self.texture is not None:
            self.texture.Draw(window, x, y, self.sizeX, self.sizeY)
        pass


class Player(Entity):
    pivotX = 0.5
    pivotY = 1
    color = (200, 0, 0)
    sizeY = 12 * 4
    sizeX = 9 * 2

    xSpeed = 0
    ySpeed = 0

    jumpRequested = False

    landed = True
    lastLanded = -5000
    jumpOffset = 0.1
    jumpForce = 800
    gravity = 1800

    isWallTouching = 0  # 0 for False and 1 or -1 according to the side
    wallSlidingRate = 0.9
    lastWalled = -5000
    lastWallDir = 0
    wallJumpOffset = 0.13
    wallJumpBoost = 400

    movSpeed = 800
    movAcc = 0.2
    movDec = 0.3

    lastHorizontalInput = 1

    animationStartTime = 0
    lastAnimation = None

    def __init__(self, x, y, game):
        super().__init__(x, y, game)
        self.normalAnim = ConvertPlayerSpriteSheet(game.execPath + "/SpriteSheet_Player.png",
                                                   4 // game.texturePixelScale)
        self.spaceAnim = ConvertPlayerSpriteSheet(game.execPath + "/SpriteSheet_Player_Astronaut.png",
                                                  4 // game.texturePixelScale)
        self.animations = self.normalAnim

        self.movSpeed //= game.texturePixelScale
        self.gravity //= game.texturePixelScale
        self.jumpForce //= game.texturePixelScale
        self.wallJumpBoost //= game.texturePixelScale

    def Update(self, game):
        # Landed
        self.landed = not game.place_free(self, self.x, self.y + 1)
        if self.landed:
            self.lastLanded = pg.time.get_ticks()

        # Gravity
        self.ySpeed += self.gravity * game.delta_time

        # Wall Slide
        left = game.place_free(self, self.x - 1, self.y)
        right = game.place_free(self, self.x + 1, self.y)
        if not left and not right:
            self.isWallTouching = game.horizontalInput
        else:
            self.isWallTouching = (not right) - (not left)
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
        if self.game.level == 3:
            self.animations = self.spaceAnim

        self.idleAnim, self.runAnim, self.jumpAnim, self.fallAnim, self.slideAnim = self.animations
        animSpeed = 0.2
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
                    animSpeed = 0.13
                else:
                    curAnimation = self.fallAnim

        if self.lastAnimation != curAnimation:
            self.animationStartTime = pg.time.get_ticks()
            self.lastAnimation = curAnimation

        if self.game.allPlaced:
            frameI = floor((pg.time.get_ticks() - self.animationStartTime) / animSpeed / 1000) % len(curAnimation)
        else:
            frameI = 0

        frame = curAnimation[frameI]
        x, y = self.x, self.y
        x, y = camera.WorldToScreen(x, y)

        w, h = frame.get_size()
        mirrored = self.lastHorizontalInput < 0
        '''if curAnimation is self.slideAnim:
            mirrored = not mirrored'''
        frame = pygame.transform.flip(frame, mirrored, False)
        window.blit(frame, (x - w / 2, y - h))
        if self.game.debug:
            super().Draw(window, camera)


class CheckPoint(Entity):
    color = (0, 230, 0)
    pivotY = 1
    pivotX = 0.5

    parentWall = None
    sizeX = 10 * 4
    sizeY = 8 * 4

    texture = None

    def __init__(self, game):
        super().__init__(0, 0, game)
        self.texture = ConvertSprite(self.game.execPath + "\checkpoint.png", self.game.texturePixelScale)

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
            dist = Distance2(newWall.desiredX - self.game.player.x, newWall.desiredY - self.game.player.y)
            if dist > maxDist:
                maxDist = dist
                selectedWall = newWall
        self.parentWall = selectedWall


    def Update(self, game):
        if game.allPlaced:
            x, y = self.GetTopLeftPoint()
            if self.game.player.BoxCollide(x, y, self.x, self.y):
                game.CheckPointObtained()
            self.x = self.parentWall.x
            self.y = self.parentWall.y + (
                    -4 - 3 * 4 + sin(pg.time.get_ticks() / 1000 * 2) * 8) / self.game.texturePixelScale

    def Draw(self, window, camera):

        if self.game.allPlaced:
            if self.game.level == 2 and self.game.checkpointTook == self.game.checkpointBeforeTimeDecrease - 1:
                sprite = self.game.player.spaceAnim[0][0]
            else:
                sprite = self.texture
            x, y = self.GetTopLeftPoint()
            x, y = camera.WorldToScreen(x, y)
            window.blit(sprite, (x, y))
            if self.game.debug:
                super().Draw(window, camera)


class Borne(Entity):
    animation = []
    morphStart = None
    startX = None
    startY = None
    startSizeX = None
    startSizeY = None

    def __init__(self, x, y, game):
        super().__init__(x, y, game)
        self.animation = ConvertBorneSpriteSheet(game.execPath + "\\sprite_Borne.png", 4 // self.game.texturePixelScale)
        self.desiredX = x
        self.desiredY = y
        self.placed = True
        self.morphDuration = 1

    def Draw(self, window, camera):
        if self.game.debug:
            super().Draw(window, camera)
        animSpeed = 0.5
        frameI = floor((pg.time.get_ticks()) / animSpeed / 1000) % len(self.animation)
        frame = self.animation[frameI]

        x, y = self.x, self.y
        x, y = camera.WorldToScreen(x, y)
        y += CustomSin(0, 30, 0.5, pg.time.get_ticks())
        w, h = frame.get_size()
        window.blit(frame, (x - w / 2, y - h))

    def StartMorph(self, duration=None):
        self.placed = False
        if duration is not None:
            self.morphDuration = duration
        else:
            self.morphDuration = 1000
        self.morphStart = pg.time.get_ticks()
        self.startX = self.x
        self.startY = self.y

    def Update(self, game):
        if not self.placed:
            curTime = pg.time.get_ticks()
            endTime = self.morphStart + self.morphDuration
            if curTime >= endTime:
                self.placed = True

            self.x = SmoothLerp(self.startX, self.desiredX, curTime, self.morphStart, endTime)
            self.y = SmoothLerp(self.startY, self.desiredY, curTime, self.morphStart, endTime)

class Camera:
    def __init__(self, x, y, WINDOW_WIDTH, WINDOW_HEIGHT):
        self.x = x
        self.y = y
        self.zoom = 1
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT

    def WorldToScreen(self, x, y):
        return (x - self.x) * self.zoom + self.WINDOW_WIDTH / 2, (y - self.y) * self.zoom + self.WINDOW_HEIGHT / 2

    def ScreenToWorld(self, x, y):
        return (x - self.WINDOW_WIDTH / 2) / self.zoom + self.x, (y - self.WINDOW_HEIGHT / 2) / self.zoom + self.y
