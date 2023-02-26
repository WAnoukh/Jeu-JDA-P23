import pygame as pg


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

    def draw(self, window, camera):
        offsetX = self.sizeX * self.pivotX
        offsetY = self.sizeY * self.pivotY
        x, y = camera.WorldToScreen(self.x, self.y)
        pg.draw.rect(window, self.color,
                     pg.Rect(x - offsetX, y - offsetY, self.sizeX, self.sizeY))

    def GetTopLeftPoint(self):
        return self.x - self.sizeX * self.pivotX, self.y - self.sizeY * self.pivotY


class Wall(Entity):
    def __init__(self, x, y, sizeX, sizeY):
        super().__init__(x, y)
        self.pivotX = 0.5
        self.pivotY = 0
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.color = (200, 200, 200)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.pivotX = 0.5
        self.pivotY = 1
        self.color = (200, 0, 0)
        self.sizeY = 25
        self.sizeX = self.sizeY


class Camera:
    def __init__(self, x, y, WINDOW_WIDTH, WINDOW_HEIGHT):
        self.x = x
        self.y = y
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT

    def WorldToScreen(self, x, y):
        return x - self.x + self.WINDOW_WIDTH / 2, y - self.y + self.WINDOW_HEIGHT / 2

    def ScreenToWorld(self, x, y):
        return x + self.x - self.WINDOW_WIDTH / 2, y + self.y - self.WINDOW_HEIGHT / 2
