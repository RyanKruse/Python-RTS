import pygame as pg
import pygame.gfxdraw
import pygame.font
from pygame.color import THECOLORS
from settings import *


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((0, 0))
        # self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE

    def get_keys(self):
        """This code is fired from get_keys, independent from game class keys."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and not keys[pygame.K_d]:
            self.x -= self.game.player_speed
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            self.x += self.game.player_speed
        if keys[pygame.K_w] and not keys[pygame.K_s]:
            self.y -= self.game.player_speed
        elif keys[pygame.K_s] and not keys[pygame.K_w]:
            self.y += self.game.player_speed

    def update(self):
        self.get_keys()
        self.rect.x = self.x
        self.rect.y = self.y


class Wall(pg.sprite.Sprite):
    """I don't know what those game.x functions are."""
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.collision_sprites, game.map_walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(THECOLORS['cornflowerblue'])
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        self.x = x  # Unknown
        self.y = y  # Unknown
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Iron(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.collision_sprites, game.map_iron
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE/2, TILESIZE/2), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = (x * TILESIZE + (TILESIZE / 4))
        self.rect.y = (y * TILESIZE + (TILESIZE / 4))

    def draw(self):
        pygame.gfxdraw.filled_circle(self.image, round(TILESIZE / 4), round(TILESIZE / 4),
                                     round(TILESIZE / 5), THECOLORS['gray'])