import pygame as pg
from pygame.sprite import Sprite
from settings import *
from pygame.math import Vector2
from pygame.color import THECOLORS
from building import *


# =============================================== Parent Class ================================================== #

class Construction(Sprite):
    """Construction delay for building cities or workshops."""
    def __init__(self, game, x, y):
        # Group information
        self.groups = game.g.all_sprites, game.g.collision_sprites, game.g.construction
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.cost = []
        self.is_built = False
        self.tick = 0
        self.alpha_surface = None

        # Image information
        self.image = pg.image.load(CITY_VALID)
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        for ghost in self.game.g.ghost_building:
            self.rect.x = ghost.rect.x
            self.rect.y = ghost.rect.y

        self.radius = CITY_MAX_RADIUS
        self.surf1 = pg.Surface((self.radius * 2, self.radius * 2))
        self.surf1.fill(TRANSPARENT)
        self.surf1.set_colorkey(TRANSPARENT)
        self.surf1.set_alpha(TERRITORY_SHADE)
        self.circle_init(x, y)

    def circle_init(self, x, y):
        pg.draw.circle(self.surf1, THECOLORS['lightcyan1'], (round((self.rect.center[0] + self.game.camera.x) + self.radius - x),
                                                      round((self.rect.center[1] + self.game.camera.y) + self.radius - y)),
                                                      self.radius)
    def draw_circle(self):
        self.game.screen.blit(self.surf1, ((self.rect.center[0] + self.game.camera.x) - self.radius,
                                                 (self.rect.center[1] + self.game.camera.y) - self.radius, 50, 50))

    def update(self):
        self.surf1.set_alpha(TERRITORY_SHADE)

        self.build_tick()
        self.build_building()

    def delete(self):
        """Deletes self after construction is complete."""
        pg.sprite.spritecollide(self, self.game.g.construction, True)

    def build_tick(self):
        self.image.set_alpha((self.tick * 75) + 25)
        self.tick += RESOURCE_TICK

    def build_building(self):
        """I am speed building cities"""
        if self.tick > CONSTRUCT_TIME:
            CityBuilding(self.game, self.rect.x, self.rect.y, self.surf1)
            self.game.resource.refresh()
            self.game.check_button_validity()
            self.delete()
