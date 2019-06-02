import pygame as pg
from pygame.sprite import Sprite
from settings import *
from sprites import *


class TowerArrow(Sprite):
    """This is an arrow projectile, spawned by tower. It can be used for friendly/foe."""
    def __init__(self, game, start_x, start_y, move_x, move_y, enemy_group):
        self.groups = game.all_sprites, game.projectiles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Image Information
        self.image = pg.image.load(TOWER_ARROW)
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        # Movement slope information.
        self.start_x = start_x
        self.start_y = start_y
        self.rect.x = start_x
        self.rect.y = start_y
        self.move_x = move_x
        self.move_y = move_y
        self.speed = TOWER_ARROW_SPEED
        self.overlap = TOWER_ARROW_EXTRA_OVERLAP
        self.buffer = TOWER_ARROW_SPEED
        self.move_slope = 0
        self.move_quadrant = 0
        self.move_counter = 0
        # Target information
        self.enemy_group = enemy_group

    def update(self):
        """This fires every single frame."""
        self.set_move_slope()
        self.collision_detection()

    def set_move_slope(self):
        """This calculates the movement toward a given target."""
        if self.game.arrived_at_location(self):
            self.overlap_decay()
        self.game.slope_movement_logic(self)

    def collision_detection(self):
        """If colliding with an enemy, deal damage and delete projectile."""
        collision = pg.sprite.spritecollide(self, self.enemy_group, False)
        for obj in collision:
            obj.health -= TOWER_ARROW_DAMAGE/len(collision)
            pg.sprite.spritecollide(self, self.game.projectiles, True)
            if obj.health <= 0:
                obj.delete()
            break

    def overlap_decay(self):
        """If projectile misses its target, it flies extra until it decays."""
        self.overlap -= 1
        if self.overlap == 0:
            pg.sprite.spritecollide(self, self.game.projectiles, True)
        self.move_x = self.rect.x + (self.move_x - self.start_x)
        self.move_y = self.rect.y + (self.move_y - self.start_y)