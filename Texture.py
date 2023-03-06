from math import floor, ceil

import pygame as pg
from PIL import Image
from main import *


def pilImageToSurface(pilImage):
    return pg.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode)


def ConvertTo9Sided(path, lMargin, uMargin, rMargin, bMargin, scale):
    inImg = Image.open(path)
    outImgs = []
    width, height = inImg.size
    xs = [0, lMargin, width - rMargin, width]
    ys = [0, uMargin, height - bMargin, height]
    for x in range(3):
        for y in range(3):
            cutImg = inImg.crop((xs[x], ys[y], xs[x + 1], ys[y + 1]))
            if x == 1 and y == 1:
                surface = pilImageToSurface(cutImg).convert()
            else:
                surface = pilImageToSurface(cutImg).convert_alpha()
            w, h = surface.get_size()
            surface = pg.transform.scale(surface, (w * scale, h * scale))
            outImgs.append(surface)
    return outImgs, width, height


def ConvertSprite(path, scale, cutBottom = 0):
    inImg = Image.open(path)
    w, h = inImg.size
    if cutBottom != 0:
        inImg = inImg.crop((0, 0, w, cutBottom))
    pilImage = pilImageToSurface(inImg)
    surface = pilImageToSurface(inImg).convert()
    w, h = surface.get_size()
    return pg.transform.scale(pilImageToSurface(inImg), (w * scale, h * scale))


def ConvertPlayerSpriteSheet(path, scale):
    inImg = Image.open(path)
    sw, sh = 9, 12
    idleLength = 4
    runLength = 2
    jumpLength = 4
    fallLength = 2
    slideLength = 1
    idleAnim, runAnim, jumpAnim, fallAnim, slideAnim = [], [], [], [], []
    y = 0
    for anim, length in [(idleAnim, idleLength), (runAnim, runLength), (jumpAnim, jumpLength), (fallAnim, fallLength),
                         (slideAnim, slideLength)]:
        for i in range(length):
            cutImg = inImg.crop((sw * i, y, sw * (i + 1), y + sh))
            surface = pilImageToSurface(cutImg).convert()
            w, h = surface.get_size()
            anim.append(pg.transform.scale(pilImageToSurface(cutImg), (w * scale, h * scale)))
        y += sh
    return idleAnim, runAnim, jumpAnim, fallAnim, slideAnim


def ConvertBorneSpriteSheet(path, scale):
    inImg = Image.open(path)
    sw, sh = 24, 34
    idleLength = 4
    idleAnim = []
    for i in range(idleLength):
        cutImg = inImg.crop((sw * i, sh, sw * (i + 1), 2 * sh))
        surface = pilImageToSurface(cutImg).convert_alpha()
        w, h = surface.get_size()
        idleAnim.append(pg.transform.scale(surface, (w * scale, h * scale)))
    return idleAnim


class Texture_9Sided:
    def __init__(self, path, lMargin, tMargin, rMargin, bMargin, scale):
        self.textures, self.w, self.h = ConvertTo9Sided(path, lMargin, tMargin, rMargin, bMargin, scale)
        self.lMargin, self.tMargin, self.rMargin, self.bMargin = lMargin, tMargin, rMargin, bMargin
        self.scale = scale

    def GetSize(self, xRepetitions, yRepetitions):
        x = ceil(((self.w - (self.rMargin + self.lMargin)) * xRepetitions + (self.rMargin + self.lMargin)) * self.scale)
        y = ceil(((self.h - (self.tMargin + self.bMargin)) * yRepetitions + (self.tMargin + self.bMargin)) * self.scale)
        return x, y

    def Draw(self, window, x, y, sizeX, sizeY, surface=None):
        scale = self.scale
        xs = [0, self.lMargin * scale, (self.w - self.rMargin) * scale, self.w * scale]
        ys = [0, self.tMargin * scale, (self.h - self.bMargin) * scale, self.h * scale]
        xMargin = self.lMargin + self.rMargin
        yMargin = self.tMargin + self.bMargin
        xRepetitions = floor((sizeX / self.scale) // (self.w - xMargin))
        yRepetitions = floor((sizeY / self.scale) // (self.h - yMargin))
        drawnY = 0
        for i in range(3):
            deltaY = ys[i + 1] - ys[i]
            for _ in [0] if i == 0 or i == 2 else range(yRepetitions):
                drawnX = 0
                for j in range(3):
                    deltaX = xs[j + 1] - xs[j]
                    for _ in [0] if j == 0 or j == 2 else range(xRepetitions):
                        if surface is None:
                            surface = window
                        surface.blit(self.textures[i + 3 * j],
                                     (x + drawnX, y + drawnY))

                        drawnX += deltaX
                drawnY += deltaY
