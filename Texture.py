import pygame as pg
from PIL import Image


def pilImageToSurface(pilImage):
    return pg.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode)


def ConvertTo9Sided(path, lMargin, uMargin, rMargin, bMargin):
    inImg = Image.open(path)
    outImgs = []
    width, height = inImg.size
    xs = [0, lMargin, width - rMargin, width]
    ys = [0, uMargin, height - bMargin, height]
    for x in range(3):
        for y in range(3):
            cutImg = inImg.crop((xs[x], ys[y], xs[x + 1], ys[y + 1]))
            outImgs.append(pilImageToSurface(cutImg))
    return outImgs, width, height


class Texture_9Sided:
    def __init__(self, path, lMargin, tMargin, rMargin, bMargin):
        self.textures, self.w, self.h = ConvertTo9Sided(path, lMargin, tMargin, rMargin, bMargin)
        self.lMargin, self.uMargin, self.rMargin, self.bMargin = lMargin, tMargin, rMargin, bMargin

    def Draw(self, window, x, y, sizeX, sizeY, scale):
        xs = [0, self.lMargin * scale, (self.w - self.rMargin) * scale, self.w * scale]
        ys = [0, self.uMargin * scale, (self.h - self.bMargin) * scale, self.h * scale]
        xMargin = self.lMargin + self.rMargin
        yMargin = self.uMargin + self.bMargin
        xRepetitions = int((sizeX / scale - xMargin) // (self.w - xMargin))
        yRepetitions = int((sizeY / scale - yMargin) // (self.h - yMargin))
        drawnY = 0
        for i in range(3):
            deltaY = ys[i + 1] - ys[i]
            for _ in [0] if i == 0 or i == 2 else range(yRepetitions):
                drawnX = 0
                for j in range(3):
                    deltaX = xs[j + 1] - xs[j]
                    for _ in [0] if j == 0 or j == 2 else range(xRepetitions):
                        window.blit(pg.transform.scale(self.textures[i + 3 * j], (deltaX, deltaY)),
                                    (x + drawnX, y + drawnY))
                        drawnX += deltaX
                drawnY += deltaY
        return xRepetitions, yRepetitions