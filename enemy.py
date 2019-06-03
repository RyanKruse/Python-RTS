import pygame as pg
from pygame.sprite import Sprite
from settings import *
from sprites import *

class EnemyUnit(Sprite):
    """This class handles enemy units."""
    def __init__(self, game):
        self.groups = game.g.all_sprites, game.g.collision_sprites, game.g.enemy_units
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Image information
        self.image = pg.image.load(UNIT_DESELECTED)
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

        # Health information
        self.health = KNIGHT_HP

    def child_init(self):
        pass

    def update(self):
        """I need an AI class one day."""
        self.collision_detection()

    def collision_detection(self):
        """If collision with another sprite occurs, this bumps us away."""
        for other in pg.sprite.spritecollide(self, self.game.g.collision_sprites, False):
            self.game.collision_bump(self, other)

    def delete(self):
        """Deletes self."""
        pg.sprite.spritecollide(self, self.game.g.enemy_units, True)


# =============================================== Child Classes ================================================== #
# Various units are included below.

class EnemyKnight(EnemyUnit):
    def __init__(self, game):
        super().__init__(game)
        # Image information.
        self.image = pg.image.load(ENEMY_KNIGHT)


