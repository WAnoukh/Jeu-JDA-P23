from math import floor

from entity import Camera, Player, Wall, Entity
from functions import lerpDt, randomRange, clamp
import pygame as pg
from pygame.locals import *
from random import random, randint


class Game:
    font = None
    jumpKeyDOWN = False
    jumpKeyPRESSED = False
    jumpKeyRELEASED = False

    horizontalInput = 0

    delta_time = 0.05

    player = None
    MainCamera = None
    camDesiredX = None
    camDesiredY = None
    walls = []
    newWalls = []
    wallAmount = 20
    allPlaced = False
    firstGeneration = True

    def __init__(self, window, WINDOW_WIDTH, WINDOW_HEIGHT):
        self.wasplaced = None
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.WINDOW = window
        self.Start()

    def Start(self):
        baseLevel = -1000
        self.player = Player(0, baseLevel, self)

        self.MainCamera = Camera(self.player.x, self.player.y, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.camDesiredX = self.player.x
        self.camDesiredY = self.player.y

        firstWall = Wall(0, baseLevel, 200, round(200 / 1.6), self, dy=baseLevel)
        self.firstGeneration = True
        self.GenerateFromWall(firstWall)
        for wall in self.walls:
            wall.StartMorph(1 * 1000)
        self.wasplaced = False

    def Update(self):
        if self.allPlaced:
            self.player.Update(self)
            if not self.wasplaced:
                self.wasplaced = True
                for wall in self.walls:
                    if not self.place_free(wall, wall.x, wall.y):
                        # print("error generation ", wall.id)
                        wall.color = (0, 0, 0)
        else:
            self.allPlaced = True
            for wall in self.walls:
                if not wall.placed:
                    self.allPlaced = False
                    wall.Update(self)

        # camera
        self.camDesiredX = lerpDt(self.camDesiredX, self.player.x, 0.9, self.delta_time)
        self.camDesiredY = lerpDt(self.camDesiredY, self.player.y, 0.9, self.delta_time)
        self.MainCamera.x = round(self.camDesiredX)
        self.MainCamera.y = round(self.camDesiredY)
        if self.player.y > 1000:
            self.Start()

    def Draw(self):
        self.WINDOW.fill((170, 200, 255))
        i = 0
        for wall in self.walls:
            wall.draw(self.WINDOW, self.MainCamera)
        self.player.draw(self.WINDOW, self.MainCamera)

        x, y = pg.mouse.get_pos()
        wx, wy = self.MainCamera.ScreenToWorld(x, y)
        testCollision = Entity(x, y, game=self)
        testCollision.sizeX, testCollision.sizeY = 10, 10
        place = self.place_free(testCollision, wx - 5, wy - 5)
        pg.draw.rect(self.WINDOW, (255 * place, 255 * (not place), 0), Rect(x - 10, y - 10, 10, 10))

    def printTextOnScreen(self, text, x, y):
        img = self.font.render(str(text), True, (255, 0, 0))
        self.WINDOW.blit(img, (x, y))

    def place_free(self, entity, x, y, newWalls=False):
        x -= entity.pivotX * entity.sizeX
        y -= entity.pivotY * entity.sizeY
        for wall in self.newWalls if newWalls else self.walls:
            if id(entity) != id(wall):
                if wall.BoxCollide(x, y, x + entity.sizeX, y + entity.sizeY):
                    return False
        return True

    def GenerateFromWall(self, wall):
        self.newWalls = [wall]

        def pickRandomWAll():
            return self.newWalls[floor(randomRange(0, len(self.newWalls) - 1))]

        i = 0
        while i < self.wallAmount:
            selectedWall = pickRandomWAll()
            # pick a side of the wall which we want to add a neighbor (0:leftside, 1:rightside, 2:topside)
            side = randint(0, 1)
            simulatedJumpLength = randomRange(0.2, 1.5)
            x, y = selectedWall.GetDesiredTopLeftPoint()
            x += side * selectedWall.desiredSizeX
            xSpeed, ySpeed = 0, -self.player.jumpForce
            simuHorizontalInput = -1 if side == 0 else 1
            simuDeltaTime = 0.05
            cumulatedTime = 0
            collided = False
            while cumulatedTime < simulatedJumpLength and not collided:

                xSpeed += simuHorizontalInput * (self.player.movSpeed / self.player.movAcc) * simuDeltaTime
                xSpeed = clamp(xSpeed, -self.player.movSpeed, self.player.movSpeed)
                x += xSpeed * simuDeltaTime
                y += ySpeed * simuDeltaTime
                ySpeed += self.player.gravity * simuDeltaTime
                if not self.place_free(self.player, x, y, newWalls=True):
                    collided = True
                cumulatedTime += simuDeltaTime
            if collided:
                continue
            h, w = randint(30, 500), randint(26, 500)
            x, y = round(x), round(y)
            newWall = Wall(x, y, w + self.player.sizeX, h + self.player.sizeY,
                           self, dx=x, dy=y, dsx=w, dsy=h)
            if not self.place_free(newWall, newWall.x, newWall.y, newWalls=True):
                continue
            self.newWalls.append(newWall)
            newWall.id = i + 1
            i += 1
        if self.firstGeneration:

            for i in range(len(self.newWalls)):
                newWall = self.newWalls[i]
                newWall.y = 1000
                newWall.sizeX = newWall.desiredSizeX
                newWall.sizeY = newWall.desiredSizeX
            self.firstGeneration = False
        else:
            for i in range(len(self.newWalls)):
                newWall = self.newWalls[i]
                oldWall = self.walls[i]
                newWall.x = oldWall.x
                newWall.y = oldWall.y
                newWall.sizeX = oldWall.sizeX
                newWall.sizeY = oldWall.sizeY
        self.walls = self.newWalls.copy()
        self.allPlaced = False
        for wall in self.walls:
            wall.StartMorph(1 * 1000)

    def Loop(self):
        self.Update()
        self.Draw()
