import pygame as pg
from pygame.sprite import Sprite
from settings import *
from sprites import *


class Unit(Sprite):
    """This class handles knights."""
    def __init__(self, game):
        self.groups = game.all_sprites, game.collision_sprites, game.units
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Image information
        self.image_deselected = pg.image.load(UNIT_DESELECTED)
        self.image_selected = pg.image.load(UNIT_DESELECTED)
        self.image = self.image_deselected
        # Location information.
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        self.rect.x = pg.mouse.get_pos()[0] - (self.size[0] / 2) - self.game.camera.x
        self.rect.y = pg.mouse.get_pos()[1] - (self.size[1] / 2) - self.game.camera.y
        # Movement slope information.
        self.move_x = 0
        self.move_y = 0
        self.move_slope = 0
        self.move_quadrant = 0
        self.move_counter = 0
        self.speed = KNIGHT_SPEED
        self.health = KNIGHT_HP
        # Boolean logic.
        self.is_selected = False
        self.is_moving = False
        self.is_hotkeyed = False

    def update(self):
        """This fires every single frame."""
        if (self.game.mouse.is_commanding and self.is_selected) or self.is_moving:
            self.set_move_slope()
        self.collision_detection()

    def set_move_location(self):
        """Defines new movement location for selected units."""
        self.move_counter = 0
        self.is_moving = True
        self.move_x = pg.mouse.get_pos()[0] - self.game.camera.x
        self.move_y = pg.mouse.get_pos()[1] - self.game.camera.y

    def set_move_slope(self):
        """This calculates the movement to a given location."""
        self.game.slope_movement_logic(self)

    def collision_detection(self):
        """If collision with another sprite occurs, this bumps us away."""
        for other in pg.sprite.spritecollide(self, self.game.collision_sprites, False):
            self.game.collision_bump(self, other)

    def set_selected(self):
        """Adds unit into the selected units group."""
        pg.sprite.Group.add(self.game.selected_units, self)
        self.is_selected = True
        self.image = self.image_selected

    def set_deselected(self):
        """Removes unit from the selected units group."""
        pg.sprite.Group.remove(self.game.selected_units, self)
        self.is_selected = False
        self.image = self.image_deselected

    def delete(self):
        """Deletes self."""
        pg.sprite.spritecollide(self, self.game.units, True)


# =============================================== Child Classes ================================================== #

class Knight(Unit):
    def __init__(self, game):
        super().__init__(game)
        # Image information.
        self.image_deselected = pg.image.load(KNIGHT_DESELECTED)
        self.image_selected = pg.image.load(KNIGHT_SELECTED)
        self.image = pg.image.load(KNIGHT_DESELECTED)
        self.health = KNIGHT_HP

