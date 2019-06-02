import pygame as pg
from pygame.sprite import Sprite
from settings import *
from pygame.math import Vector2
from pygame.color import THECOLORS
from projectile import *
import random


class Building(Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites, game.collision_sprites, game.buildings
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.cost = []
        self.refund_amount = []
        # Image information
        self.image = pg.image.load(BLANK_BUILDING)
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()

    def update(self):
        """This fires every single frame."""
        self.child_update()

    def child_inits(self, image, food_cost, iron_cost, gold_cost, food_refund, iron_refund, gold_refund):
        """Fills out the inits for child classes."""
        self.image = pg.image.load(image)
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        for ghost in self.game.ghost_building:
            self.rect.centerx = ghost.rect.centerx
            self.rect.centery = ghost.rect.centery
        self.cost = [food_cost, iron_cost, gold_cost]
        self.refund_amount = [food_refund, iron_refund, gold_refund]
        self.child_inits_specific()

    def delete(self):
        """Deletes self."""
        pg.sprite.spritecollide(self.game.mouse, self.game.buildings, True)

    def child_update(self):
        """Specific updates for child classes."""
        pass

    def child_inits_specific(self):
        """Specific inits for child classes."""
        pass

    def refund_resources(self):
        """Refunds resources based on child class."""
        pass


# =============================================== Child Classes ================================================== #

class CityBuilding(Building):
    def __init__(self, game, x, y, surf1):
        super().__init__(game)
        self.child_inits(CITY_VALID, CITY_F, CITY_I, CITY_G, CITY_F_R, CITY_I_R, CITY_G_R)
        pg.sprite.Group.add(self.game.cities, self)
        self.radius = CITY_START_RADIUS
        self.surf1 = surf1
        self.rect.x = x
        self.rect.y = y

    def child_update(self):
        if self.radius < CITY_MAX_RADIUS:
            self.radius += 2

    def draw_circle(self):
        pg.draw.circle(self.game.screen, THECOLORS['lightcyan1'],
                       ((self.rect.center[0] + self.game.camera.x), (self.rect.center[1] + self.game.camera.y)),
                       round(self.radius), 3)

    def draw_territory(self):
        self.surf1.set_alpha(25)
        self.game.screen.blit(self.surf1, ((self.rect.center[0] + self.game.camera.x) - CITY_MAX_RADIUS,
                                                     (self.rect.center[1] + self.game.camera.y) - CITY_MAX_RADIUS, 0, 0))


class WallBuilding(Building):
    """Major experimenting. Do walls today."""
    def __init__(self, game):
        super().__init__(game)
        self.child_inits(WALL_VALID, WALL_F, WALL_I, WALL_G, WALL_F_R, WALL_I_R, WALL_G_R)
        pg.sprite.Group.add(self.game.walls, self)
        self.radius = 400
        self.collided_circle = None

    def child_update(self):
        """ This lags
        self.collided_circle = pg.sprite.groupcollide(
            self.game.walls, self.game.walls, False, False,
            collided=self.game.circol)
        """

    def radius_draw(self):
        for collided in self.collided_circle:
            pg.draw.circle(self.game.screen, THECOLORS['lightcyan1'],
                           ((collided.rect.center[0] + self.game.camera.x), (collided.rect.center[1] + self.game.camera.y)),
                           collided.radius, 1)


class TowerBuilding(Building):
    def __init__(self, game):
        super().__init__(game)
        self.child_inits(TOWER_VALID, TOWER_F, TOWER_I, TOWER_G, TOWER_F_R, TOWER_I_R, TOWER_G_R)
        pg.sprite.Group.add(self.game.towers, self)
        pg.sprite.Group.remove(self.game.collision_sprites, self)
        self.colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(self.colorkey)
        self.radius = TOWER_RADIUS
        self.enemies_in_range = None

    def child_update(self):
        self.shoot_enemies()

    def child_inits_specific(self):
        """Rotate the tower."""
        self.image = pg.transform.rotate(self.image.convert(), 45)
        self.rect.x -= 13
        self.rect.y -= 13
        self.rect.width += 27
        self.rect.height += 27

    def shoot_enemies(self):
        """This shoots bullets at enemy groups."""
        self.enemies_in_range = None
        self.enemies_in_range = pg.sprite.spritecollide(self, self.game.enemy_units, False, collided=self.game.circol)
        if self.enemies_in_range:
            for enemy in self.enemies_in_range:
                """We only want to shoot the first enemy"""
                if random.randint(1, TOWER_SHOOT_LIKELIHOOD) == 1:
                    TowerArrow(self.game, self.rect.centerx, self.rect.centery, enemy.rect.centerx, enemy.rect.centery,
                               self.game.enemy_units)
                break


class PlateBuilding(Building):
    def __init__(self, game, image, rect, size):
        super().__init__(game)
        pg.sprite.Group.add(self.game.plates, self)
        pg.sprite.Group.remove(self.game.all_sprites, self)
        self.child_inits(image, WALL_F, WALL_I, WALL_G, WALL_F_R, WALL_I_R, WALL_G_R)
        self.rect = rect
        self.size = size
        self.image.set_alpha(500)

    def child_inits(self, image, food_cost, iron_cost, gold_cost, food_refund, iron_refund, gold_refund):
        """Plates has its own child_inits because it is unqiue from other buildigns."""
        self.image = image
        self.cost = [food_cost, iron_cost, gold_cost]
        self.refund_amount = [food_refund, iron_refund, gold_refund]