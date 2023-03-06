from math import floor, sin, ceil, atan2, degrees

from entity import Camera, Player, Wall, Entity, CheckPoint, Borne, DecorativeWAll
from functions import lerpDt, randomRange, clamp, Normalise, Magnitude, SmoothLerp, SmoothStep, CustomSin
import pygame as pg
from pygame.locals import *
from random import random, randint
from Texture import Texture_9Sided, ConvertSprite
from ScoreManager import ScoreBoard, Score

pg.font.init()


class Game:
    execPath = "./games/ArcadiApocalypse"
    execPath = "."

    score = None
    scoreGain = None
    checkpointTook = None
    minRemainingTime = 10.0
    remainingTimeDecrease = 2.5
    initialRemainingTime = minRemainingTime + remainingTimeDecrease*5
    checkpointBeforeTimeDecrease = 5
    LevelTimeRemaining = initialRemainingTime
    remainingTime = LevelTimeRemaining

    morphFirstDuration = 3
    morphDuration = 1

    jumpKeyDOWN = False
    jumpKeyPRESSED = False
    jumpKeyRELEASED = False

    horizontalKeyPressed = False
    verticalKeyPressed = False
    greenPressed = False
    bluePressed = False
    purplePressed = False

    horizontalInput = 0
    verticalInput = 0

    delta_time = 0.05

    borne = None

    player = None
    dead = False
    MainCamera = None
    checkpoint = None

    camDesiredX = None
    camDesiredY = None
    camTarget = None
    walls = []
    newWalls = []
    wallAmount = 12
    allPlaced = False
    firstGeneration = True

    decorativeWall = []
    decorativeWallAmount = 10

    wallTexture = None
    arrowTexture = None

    deathAltitude = 1000

    debug = False

    scoreBoard = None

    mainMenu = True

    endMenu = False
    endMenuSince = 0
    endMenuY = 0

    entryNumber = 8
    entrySelected = 0
    entryValues = [1, 14, 15, 14, 25, 13] + [0 for i in range(entryNumber - 3)]
    entryMode = [1] + [0 for _ in range(entryNumber - 1)]
    entryValuesCharLetter = " abcdefghijklmnopqrstuvwxyz"
    entryValuesCharMajLetter = entryValuesCharLetter.upper()
    entryValuesCharNum = " 0123456789"

    def __init__(self, window, WINDOW_WIDTH, WINDOW_HEIGHT, texturePixelScale):
        self.texturePixelScale = texturePixelScale

        self.wasPlaced = None
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.WINDOW = window

        self.wallTexturePath = self.execPath + "/9Sided_Wall.png"
        self.wallTexture = Texture_9Sided(self.wallTexturePath, 6, 6, 6, 6, (4 // texturePixelScale))
        self.decorativeWallTexture = Texture_9Sided(self.wallTexturePath, 6, 6, 6, 6, (4 // texturePixelScale))
        self.arrowTexture = ConvertSprite(self.execPath + "/arrow.png", 4 // texturePixelScale)
        self.BGTexture = ConvertSprite(self.execPath + "/fond_seamless.png", 4 // texturePixelScale)
        self.BGSpaceTexture = ConvertSprite(self.execPath + "/fond_seamless.png", 4 // texturePixelScale, cutBottom=451)
        self.scoreBoard = ScoreBoard(self.execPath + "/Score.json")

        self.fontScore = pg.font.Font(self.execPath + "/RetroGaming.ttf", 50 // texturePixelScale)
        self.fontTopScore = pg.font.Font(self.execPath + "/RetroGaming.ttf", 40 // texturePixelScale)
        self.fontScoreSmall = pg.font.Font(self.execPath + "/RetroGaming.ttf", 20 // texturePixelScale)
        self.fontGameOver = pg.font.Font(self.execPath + "/RetroGaming.ttf", 150 // texturePixelScale)
        self.fontButton = pg.font.Font(self.execPath + "/RetroGaming.ttf", 25 // texturePixelScale)
        self.fontTitle = pg.font.Font(self.execPath + "/font_Title.ttf", 120 // texturePixelScale)
        self.fontDebug = pg.font.Font(self.execPath + "/RetroGaming.ttf", 50 // texturePixelScale)

        self.blueImg = ConvertSprite(self.execPath + "/b_blue.png", 2 // texturePixelScale)
        self.greenImg = ConvertSprite(self.execPath + "/b_green.png", 2 // texturePixelScale)
        self.purpleImg = ConvertSprite(self.execPath + "/b_purple.png", 2 // texturePixelScale)
        self.redImg = ConvertSprite(self.execPath + "/b_red.png", 2 // texturePixelScale)

        self.endMenuStartY = -50

        self.PreStart()

    def PreStart(self):
        self.level = 0
        self.deathAltitude = 1000 // self.texturePixelScale
        self.dead = False

        baseLevel = self.deathAltitude - 2000 // self.texturePixelScale
        self.player = Player(0, baseLevel, self)
        self.borne = Borne(0, baseLevel - 350 // self.texturePixelScale, self)

        self.MainCamera = Camera(self.player.x, self.player.y, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.camDesiredX = self.player.x
        self.camDesiredY = self.player.y

        w, h = self.wallTexture.GetSize(2, 1)
        self.walls = [Wall(0, baseLevel, w, h, self, dy=baseLevel)]

        for i in range(self.decorativeWallAmount):
            self.decorativeWall.append(DecorativeWAll(self))

        self.camTarget = self.player

        # self.Start()

    def Start(self):
        self.dead = False
        deathAltitude = 1000
        self.firstGeneration = True
        #self.entryValues = [1, 14, 15, 14, 25, 13] + [0 for i in range(self.entryNumber - 3)]
        while not self.GenerateFromWall(self.walls[0]):
            pass
        for wall in self.walls:
            wall.StartMorph(self.morphDuration * 1000)
        self.wasPlaced = False

        self.score = 0
        self.scoreGain = 500
        self.checkpointTook = 0
        self.remainingTimeDecrease = 5
        self.LevelTimeRemaining = self.initialRemainingTime
        self.remainingTime = self.LevelTimeRemaining

        self.checkpoint = CheckPoint(self)
        self.checkpoint.Start()
        self.BorneStartMouvement()

    def Update(self):
        if self.mainMenu:
            self.MainCamera.y = -1300 // self.texturePixelScale
            self.camDesiredY = self.MainCamera.y
            if self.jumpKeyPRESSED:
                self.mainMenu = False
                self.Start()
            pass
        else:
            '''if self.borne is not None:
                self.borne.y -= 300 * self.delta_time
                if self.borne.y < self.MainCamera.y - self.WINDOW_HEIGHT / 2:
                    self.borne = None'''
            self.borne.Update(self)

            if self.remainingTime < 0 and not self.dead:
                self.KillPlayer()
                self.remainingTime = 0

            self.checkpoint.Update(self)

            if self.allPlaced:
                if not self.dead:
                    self.player.Update(self)
                if not self.wasPlaced:
                    self.wasPlaced = True
                    for wall in self.walls:
                        if not self.place_free(wall, wall.x, wall.y):
                            wall.color = (0, 0, 0)
            else:
                self.allPlaced = True
                for wall in self.walls:
                    if not wall.placed:
                        self.allPlaced = False
                        wall.Update(self)

            # camera
            # self.MainCamera.zoom = sin(pg.time.get_ticks() / 1000) * 0.5 + 1
            if not self.allPlaced and not self.firstGeneration:
                speed = 0.9999
            else:
                speed = 0.99
            self.camDesiredX = lerpDt(self.camDesiredX, self.camTarget.x, speed, self.delta_time * self.MainCamera.zoom)
            self.camDesiredY = lerpDt(self.camDesiredY, self.camTarget.y, speed, self.delta_time * self.MainCamera.zoom)
            self.MainCamera.x = round(self.camDesiredX)
            self.MainCamera.y = round(self.camDesiredY)

            # self.camTarget = self.walls[randint(0, len(self.walls) - 1)]

            if self.allPlaced and not self.dead:
                self.camDesiredY = min(self.deathAltitude - self.WINDOW_HEIGHT, self.camDesiredY)
                if self.player.y > self.deathAltitude:
                    self.KillPlayer()
                self.remainingTime -= self.delta_time

            if self.endMenu:
                self.endMenuY = SmoothLerp(self.endMenuStartY, 0, pg.time.get_ticks(), self.endMenuSince,
                                           self.endMenuSince + 1 * 1000)
                if self.horizontalKeyPressed:
                    self.entrySelected += int(self.horizontalInput)
                    self.entrySelected %= self.entryNumber
                if self.verticalKeyPressed:
                    self.entryValues[self.entrySelected] = (self.entryValues[self.entrySelected] + self.verticalInput)
                if self.greenPressed:
                    self.entryMode[self.entrySelected] = 1 if self.entryMode[self.entrySelected] != 1 else 0
                if self.bluePressed:
                    self.entryMode[self.entrySelected] = 2 if self.entryMode[self.entrySelected] != 2 else 0
                    if self.entryValues[self.entrySelected] % len(self.entryValuesCharNum) == 0 and self.entryMode[
                        self.entrySelected] == 2:
                        self.entryValues[self.entrySelected] = 1
                if self.purplePressed:
                    self.endMenu = False
                    newScore = Score(self.score, self.GetEntryName())
                    self.scoreBoard.AddScore(newScore)
                    self.endMenu = False
                    self.mainMenu = True
                    self.PreStart()

    def DrawBG(self):
        text = self.BGTexture
        self.WINDOW.fill((255, 255, 255))
        parallax = 5
        w, h = text.get_size()
        viewX = + (- self.MainCamera.x / parallax)
        x = round(viewX) % w - 1.1 * (w) / 4
        y = -self.MainCamera.y / parallax - h * 0.775
        if y >= 0:
            text2 = self.BGSpaceTexture
            h2 = text2.get_size()[1]
            viewY = + (- self.MainCamera.y / parallax + h * 0.2)
            y2 = round(viewY) % h2
            self.WINDOW.blit(text2, (x, y2))
            self.WINDOW.blit(text2, (x - w, y2))
            self.WINDOW.blit(text2, (x, y2 - h2))
            self.WINDOW.blit(text2, (x - w, y2 - h2))
            pass
        self.WINDOW.blit(text, (x, y))
        self.WINDOW.blit(text, (x - w, y))

    def Draw(self):
        self.DrawBG()

        if self.mainMenu:
            s = pg.Surface((255, 90), pg.SRCALPHA)  # per-pixel alpha
            s.fill((0, 0, 0, 200))  # notice the alpha value in the color
            self.WINDOW.blit(s, (self.WINDOW_WIDTH * 0.01 - 4, self.WINDOW_HEIGHT / 2.5 - 4))
            self.DrawScoreBoard(self.WINDOW_WIDTH * 0.01, self.WINDOW_HEIGHT / 2.5, small=True)
            text, img = ("Bouton rouge: Commencer", self.redImg)
            font = self.fontButton
            iw, ih = img.get_size()
            hiw = iw / 2
            margin = 40 // self.texturePixelScale + hiw
            bw = font.size(text)[0] + margin
            x, y = (self.WINDOW_WIDTH - bw) / 2, self.WINDOW_HEIGHT * 0.94 + self.endMenuY
            # pg.draw.rect(self.WINDOW, (0, 0, 0,50), Rect(x+2, y-4, hiw + bw, ih+8))
            s = pg.Surface((hiw + bw, ih + 8), pg.SRCALPHA)  # per-pixel alpha
            s.fill((0, 0, 0, 200))  # notice the alpha value in the color
            self.WINDOW.blit(s, (x + 2, y - 4))

            self.WINDOW.blit(img, (x + hiw, y))
            self.printTextOnScreen(text, x + margin, y + 4 // self.texturePixelScale, font=font)

        if self.mainMenu:
            font = self.fontTitle
            title = "ARCADIAPOCALYPSE"
            partialTitle = "ARCADI"
            w, h = font.size(title)
            self.printTextOnScreen(title, (self.WINDOW_WIDTH - w) / 2, self.WINDOW_HEIGHT * 0.1, font=font,
                                   color=(198, 0, 69))
            self.printTextOnScreen(partialTitle, (self.WINDOW_WIDTH - w) / 2, self.WINDOW_HEIGHT * 0.1, font=font,
                                   color=(255, 183, 62))

        if not self.dead:
            self.player.Draw(self.WINDOW, self.MainCamera)
        for wall in self.walls:
            wall.Draw(self.WINDOW, self.MainCamera)

        if self.debug:
            x, y = pg.mouse.get_pos()
            wx, wy = self.MainCamera.ScreenToWorld(x, y)
            testCollision = Entity(x, y, game=self)
            testCollision.sizeX, testCollision.sizeY = 10, 10
            place = self.place_free(testCollision, wx - 5, wy - 5)

            pg.draw.rect(self.WINDOW, (255 * place, 255 * (not place), 0), Rect(x - 10, y - 10, 10, 10))

        if not self.mainMenu:
            if self.allPlaced:
                self.checkpoint.Draw(self.WINDOW, self.MainCamera)
                if not self.dead:
                    px, py = self.player.GetCenter()
                    cx, cy = self.checkpoint.GetCenter()
                    mag = Magnitude(cx - px, cy - py)
                    x, y = (cx - px) / mag, (cy - py) / mag
                    dist = min(70, mag - 30)
                    x, y = px + x * dist, py + y * dist
                    x, y = self.MainCamera.WorldToScreen(x, y)
                    rotated_image = pg.transform.rotate(self.arrowTexture, degrees(atan2(-(cy - py), cx - px)))
                    alpha = (SmoothStep(mag, 40, 160)) * 255
                    rotated_image.set_alpha(alpha)
                    w, h = rotated_image.get_size()
                    self.WINDOW.blit(rotated_image, (x - w / 2, y - h / 2))
                    if self.debug:
                        pg.draw.rect(self.WINDOW, (0, 255, 0), Rect(x, y, 6, 6))

            if not self.dead:
                scoreToBeat, top = self.scoreBoard.NextScore(self.score)
                scoreText = "Score: " + '{:,}'.format(self.score).replace(",", " ") + " (Top {})".format(top)
                w = self.fontScore.size(scoreText)[0]
                s = pg.Surface((w+8, 90), pg.SRCALPHA)  # per-pixel alpha
                s.fill((0, 0, 0, 100))  # notice the alpha value in the color
                self.WINDOW.blit(s, (2, 10))


                # self.DrawScoreBoard(self.WINDOW_WIDTH, 50 // self.texturePixelScale, True, True)

                self.printTextOnScreen(
                    scoreText,
                    10 // self.texturePixelScale, 20 // self.texturePixelScale,
                    font=self.fontScore)

                if scoreToBeat is None:
                    self.printTextOnScreen("Highest Score !",
                                           10 // self.texturePixelScale, 70 // self.texturePixelScale,
                                           font=self.fontTopScore)
                else:
                    self.printTextOnScreen("Score to beat: " + '{:,}'.format(scoreToBeat).replace(",", " "),
                                           10 // self.texturePixelScale, 70 // self.texturePixelScale,
                                           font=self.fontTopScore)

                self.printTextOnScreen("{:.2f}".format(self.remainingTime), 10 // self.texturePixelScale,
                                       115 // self.texturePixelScale, font=self.fontScore)


        if self.borne is not None:
            self.borne.Draw(self.WINDOW, self.MainCamera)

        if self.endMenu:

            margins = self.WINDOW_WIDTH * 0
            x, y = margins, margins + self.endMenuY
            w, h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
            pg.draw.rect(self.WINDOW, (20, 20, 20), Rect(x, y, w, h))

            font = self.fontGameOver
            fw, fh = font.size("Game Over")
            self.printTextOnScreen("Game Over", self.WINDOW_WIDTH / 2 - fw / 2,
                                   y + 120 // self.texturePixelScale - fh / 2, font=font)
            font = self.fontScore
            text = "Votre score: {}".format(self.score)
            fw2, fh2 = font.size(text)
            self.printTextOnScreen(text, self.WINDOW_WIDTH / 2 - fw2 / 2,
                                   y + 25 // self.texturePixelScale + fh - fh2 / 2, font=font)

            entryW = 100 // self.texturePixelScale
            entryH = 120 // self.texturePixelScale
            entrySpace = 30 // self.texturePixelScale
            entryY = 790 // self.texturePixelScale + self.endMenuY
            entryTotalW = entryW * self.entryNumber + entrySpace * (self.entryNumber - 1)

            text = "Entrez votre nom:"

            self.printTextOnScreen(text, self.WINDOW_WIDTH / 2 - entryTotalW / 2, entryY - 85 // self.texturePixelScale,
                                   font=font)

            for i in range(self.entryNumber):
                x = self.WINDOW_WIDTH / 2 - entryTotalW / 2 + i * (entryW + entrySpace)
                y = entryY
                if self.entrySelected == i:
                    size = CustomSin(15 // self.texturePixelScale, 20 // self.texturePixelScale, 1, pg.time.get_ticks())
                    pg.draw.rect(self.WINDOW, (200, 50, 50),
                                 Rect(x - size, y - size, entryW + size * 2, entryH + size * 2))
                pg.draw.rect(self.WINDOW, (50, 50, 50), Rect(x, y, entryW, entryH))
                font = self.fontScore
                text = self.GetEntryValue(i)
                fw, fh = font.size(text)
                self.printTextOnScreen(text, x + entryW / 2 - fw / 2, y + entryH / 2 - fh / 2, font=font)

            # self.WINDOW.blit(self.blueImg, (self.WINDOW_WIDTH / 2 -tw/2, self.WINDOW_HEIGHT * 0.7))
            buttonInfo = [("Bouton vert: Majuscules", self.greenImg), ("Bouton bleu: Chiffres", self.blueImg),
                          ("Bouton violet: Valider", self.purpleImg)]
            i = 0
            font = self.fontButton
            accx = 0
            for text, img in buttonInfo:
                x, y = 50 // self.texturePixelScale, self.WINDOW_HEIGHT * 0.94 + self.endMenuY
                self.WINDOW.blit(img, (x + accx, y))
                textMargin = 40 // self.texturePixelScale
                self.printTextOnScreen(text, x + accx + textMargin, y + 4 // self.texturePixelScale, font=font)
                accx += img.get_size()[0] + textMargin + font.size(text)[0]
                i += 1

            self.DrawScoreBoard(self.WINDOW_WIDTH / 2 - entryTotalW / 2, self.endMenuY + 270 // self.texturePixelScale)

        self.printTextOnScreen(1 / self.delta_time, 0, 0, color=(255, 0, 0))

    def DrawScoreBoard(self, x, y, small=False, leftAlign=True):
        color = (200, 200, 200)
        sColors = [(255, 183, 62), (198, 0, 69), (236, 88, 0), color, color]
        if small:
            font = self.fontScoreSmall
        else:
            font = self.fontScore
        text = "Top 5"
        h = font.size(text)[1]
        self.printTextOnScreen(text, x, y, font=font, color=color)
        maxScoreW = None
        i = 0
        for score in self.scoreBoard.Top5():
            text = score.userName
            self.printTextOnScreen(text, x + 50 // self.texturePixelScale, y + h, font=font, color=sColors[i])
            text = '  {:,}'.format(score.score).replace(",", " ")
            sw, sh = font.size(text)
            if maxScoreW is None:
                maxScoreW = sw
            spacew = font.size("aaaaaaaaaaaaaaaaa")[0]
            self.printTextOnScreen(":", x + spacew, y + h, font=font, color=color)
            intensity = 255 - i * 25
            self.printTextOnScreen(text, x + spacew + maxScoreW - sw, y + h, font=font,
                                   color=(intensity, intensity, intensity))
            h += sh
            i += 1

    def GetEntryValue(self, n):
        if self.entryMode[n] == 0:
            charList = self.entryValuesCharLetter
        elif self.entryMode[n] == 1:
            charList = self.entryValuesCharMajLetter
        else:
            charList = self.entryValuesCharNum
        return charList[self.entryValues[n] % len(charList)]

    def GetEntryName(self):
        text = ""
        for i in range(self.entryNumber):
            text += self.GetEntryValue(i)
        return text

    def SpawnEndMenu(self):
        if not self.endMenu:
            self.endMenu = True
            self.endMenuSince = pg.time.get_ticks()
            self.endMenuStartY = self.WINDOW_HEIGHT

    def KillPlayer(self):
        if not self.dead:
            self.SpawnEndMenu()
            self.dead = True

    def BorneStartMouvement(self):
        self.borne.desiredX = self.checkpoint.parentWall.desiredX
        self.borne.desiredY = self.checkpoint.parentWall.desiredY - 130
        self.borne.StartMorph(3 * 1000)

    def CheckPointObtained(self):
        # self.Checkpoint.Replace()
        self.score += self.scoreGain + ceil(self.remainingTime * (self.level + 1))
        self.checkpointTook += 1
        if self.checkpointTook >= self.checkpointBeforeTimeDecrease:
            self.deathAltitude -= 7000 // self.texturePixelScale
            self.checkpointTook = 0
            self.level += 1
            self.GenerateFromWall(self.checkpoint.parentWall)
            if self.LevelTimeRemaining > self.minRemainingTime:
                self.LevelTimeRemaining = max(self.minRemainingTime,
                                              self.LevelTimeRemaining - self.remainingTimeDecrease)
            self.scoreGain = int(pow(self.scoreGain, 1.02))
        self.remainingTime = self.LevelTimeRemaining
        self.checkpoint.Replace()
        self.BorneStartMouvement()


    def printTextOnScreen(self, text, x, y, font=None, color=(255, 255, 255)):
        if font is None:
            font = self.fontDebug
        img = font.render(str(text), True, color)
        self.WINDOW.blit(img, (x, y))

    def place_free(self, entity, x, y, newWalls=False):
        x -= entity.pivotX * entity.sizeX
        y -= entity.pivotY * entity.sizeY
        for wall in self.newWalls if newWalls else self.walls:
            if id(entity) != id(wall):
                if wall.BoxCollide(x, y, x + entity.sizeX, y + entity.sizeY):
                    return False
        return True

    def GenerateFromWall(self, inWall):
        if not self.firstGeneration:
            newX = randint(-500, 500)
        else:
            newX = 0
        newY = self.deathAltitude - 2000 // self.texturePixelScale
        wall = Wall(newX, newY, inWall.sizeX, inWall.sizeY, self, newX, newY)
        wall.isLinkedToPlayer = True
        wall.playerRelativeX = self.player.x - inWall.x
        wall.playerRelativeY = self.player.y - inWall.y
        self.newWalls = [wall]
        index = self.walls.index(inWall)
        self.walls.insert(0, self.walls.pop(index))

        def pickRandomWAll():
            return self.newWalls[floor(randomRange(0, len(self.newWalls) - 1))]

        i = 0
        tryCount = -1
        failed = False
        while i < self.wallAmount:
            tryCount += 1
            if tryCount > self.wallAmount * 1000:
                failed = True
                break
            selectedWall = pickRandomWAll()
            # pick a side of the wall which we want to add a neighbor (0:leftside, 1:rightside, 2:topside)
            side = randint(0, 1)
            simulatedJumpLength = randomRange(0.5, 1)
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
            maxW, maxH = 4, 10
            w, h = randint(0, maxW), randint(0, maxH)
            if h == 0 or w == 0 and random() < 0.85:
                w, h = randint(1, maxW), randint(1, maxH)
            xOffset, yOffset = 0, 0.1 + random() * 0.8
            w, h = self.wallTexture.GetSize(w, h)
            x, y = round(x - xOffset * w), round(y - yOffset * h)
            hpw, hph = self.player.sizeX * 1.2, self.player.sizeY * 1.2
            newWall = Wall(x - ceil(hpw / 2), y - ceil(hph / 2), w + hpw,
                           h + hph,
                           self, dx=x, dy=y, dsx=w, dsy=h)
            if not self.place_free(newWall, newWall.x, newWall.y, newWalls=True):
                continue
            self.newWalls.append(newWall)
            newWall.id = i + 1
            i += 1
        if failed:
            return False
        if self.firstGeneration:
            for i in range(len(self.newWalls)):
                newWall = self.newWalls[i]
                newWall.x = newWall.desiredX
                if i == 0:
                    pass
                else:
                    newWall.y = self.deathAltitude
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
            wall.StartMorph(self.morphFirstDuration * 1000)
        return True

    def Loop(self):
        self.Update()
        self.Draw()
