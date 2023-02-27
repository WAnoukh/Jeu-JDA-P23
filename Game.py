from math import floor

from entity import Camera, Player, Wall
from functions import lerpDt, randomRange, clamp
import pygame as pg
from pygame.locals import *
from random import random, randint


class Game:
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
    wallAmount = 10
    allPlaced = False
    firstGeneration = True

    def __init__(self, window, WINDOW_WIDTH, WINDOW_HEIGHT):
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.WINDOW = window
        self.Start()


    def Start(self):
        baseLevel = -1000
        self.player = Player(0, baseLevel)

        self.MainCamera = Camera(self.player.x, self.player.y, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.camDesiredX = self.player.x
        self.camDesiredY = self.player.y

        firstWall = Wall(0, baseLevel, 200, round(200 / 1.6), dy=baseLevel)
        self.firstGeneration = True
        self.GenerateFromWall(firstWall)
        for wall in self.walls:
            wall.StartMorph(1 * 1000)

    def Update(self):
        if self.allPlaced:
            self.player.Update(self)
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
        self.WINDOW.fill((255, 255, 255))
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
            if wall.PointCollide(x, y) or \
                    wall.PointCollide(x + entity.sizeX, y) or \
                    wall.PointCollide(x, y + entity.sizeY) or \
                    wall.PointCollide(x + entity.sizeY, y + entity.sizeY):
                return False
        return True

    def place_free_generation(self, entity, x, y, wall=False):
        sizeX, sizeY = entity.desiredSizeX if wall else entity.sizeX, entity.desiredSizeY if wall else entity.sizeY
        x -= entity.pivotX * sizeX
        y -= entity.pivotY * sizeY
        for wall in self.newWalls:
            if wall.PointDesiredCollide(x, y) or \
                    wall.PointDesiredCollide(x + sizeX, y) or \
                    wall.PointDesiredCollide(x, y + sizeY) or \
                    wall.PointDesiredCollide(x + sizeY, y + sizeY):
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
                if not self.place_free_generation(self.player, x, y, False):
                    collided = True
                cumulatedTime += simuDeltaTime
            if collided:
                continue
            h, w = randomRange(30, 500), randomRange(26, 500)
            newWall = Wall(0, -1000, 0, 0, dx=x, dy=y, dsx=w, dsy=h)
            if not self.place_free_generation(newWall, x, y, wall=True):
                continue
            self.newWalls.append(newWall)
            i += 1
        if self.firstGeneration:
            self.firstGeneration = False
        else:
            for i in range(len(self.newWalls)):
                newWall = self.newWalls[i]
                oldWall = self.walls[i]
                newWall.x = oldWall.x
                newWall.y = oldWall.y
                newWall.sizeX = oldWall.sizeX
                newWall.sizeY = oldWall.sizeY
            print("regenerated from old")
        self.walls = self.newWalls.copy()
        self.allPlaced = False
        for wall in self.walls:
            wall.StartMorph(1 * 1000)

    def Loop(self):
        self.Update()
        self.Draw()
