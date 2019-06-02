import pygame as pg
from settings import *


class Map:
    def __init__(self, filename):
        # Reads the data from the string file.
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])  # Gets length of rows in string file
        self.tileheight = len(self.data)  # Gets length of columns in string file
        self.width = self.tilewidth * TILESIZE  # Actual width is the row length multiplied by tile size.
        self.height = self.tileheight * TILESIZE  # Actual height is the column length multiplied by tile size.


class Camera:
    def __init__(self, map_width, map_height):
        self.camera = pg.Rect(0, 0, map_width, map_height)
        self.width = map_width
        self.height = map_height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        self.x = -target.rect.x + int(SCREEN_WIDTH / 2)
        self.y = -target.rect.y + int(SCREEN_HEIGHT / 2)
        self.camera = pg.Rect(self.x, self.y, self.width, self.height)