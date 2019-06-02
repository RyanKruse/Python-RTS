import pygame as pg
from pygame.sprite import Sprite
from settings import *
from building import *
from construction import *
from unit import *
import math
import random
# Put this into the __init__ to see the effects.
# self.colorkey = self.image.get_at((0, 0)) - this can make the image transparent based on pixel!
# self.image.set_colorkey(self.colorkey)


# =============================================== Parent Class ================================================== #

class Ghost(Sprite):
    def __init__(self, game):
        # Group information
        # self.groups = game.all_sprites, game.ghosts
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.cost = []

        # Image information
        self.image_valid = pg.image.load(BLANK_BUILDING)
        self.image_invalid = pg.image.load(BLANK_BUILDING)
        self.image = self.image_valid

        # Location mapping
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        self.rect.x = pg.mouse.get_pos()[0] - (self.size[0] / 2) - self.game.camera.x
        self.rect.y = pg.mouse.get_pos()[1] - (self.size[1] / 2) - self.game.camera.y
        self.is_valid = True
        self.alpha_surface = None

    def update(self):
        """This fires every single frame."""
        self.update_rect()
        self.check_valid()
        self.child_update()

    def child_init(self, building_valid, building_invalid):
        """Child class initializations."""
        self.game.all_sprites.add(self)
        self.image_valid = pg.image.load(building_valid)
        self.image_invalid = pg.image.load(building_invalid)
        self.image = self.image_valid
        self.rect = self.image.get_rect()
        self.size = self.image.get_rect().size
        self.game.is_ghost_building = True

    def update_rect(self):
        """Updates the rect of the image. Makes it transparent."""
        self.rect.x = pg.mouse.get_pos()[0] - (self.size[0] / 2) - self.game.camera.x
        self.rect.y = pg.mouse.get_pos()[1] - (self.size[1] / 2) - self.game.camera.y
        self.image.set_alpha(TRANSPARENCY)

    def delete(self):
        """Deletes self."""
        pg.sprite.spritecollide(self, self.game.ghost_building, True)

    def collision_detection(self, any_colliding, city_territory=None, wall_colliding=None):
        """Checks ghost to see if it is valid. If obstacle detected, it's invalid."""
        if (any_colliding or wall_colliding or not city_territory) and self.image == self.image_valid:
            self.image = self.image_invalid
            self.is_valid = False
            self.hide_color_key()
        elif (not any_colliding and city_territory and not wall_colliding) and self.image == self.image_invalid:
            self.image = self.image_valid
            self.is_valid = True

    def construction_calculations(self, building, *proxy_cost):
        self.game.stats.subtract_resources(self.cost)

    def check_valid(self):
        """This is too complicated for the parent class since each child has unique collision requirements."""
        pass

    def child_update(self):
        pass

    def draw_circle(self):
        pass

    def activate_runner(self):
        pass

    def hide_color_key(self):
        pass

# =============================================== Child Classes ================================================== #

class CityGhost(Ghost):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(CITY_VALID, CITY_INVALID)
        self.cost = [CITY_F, CITY_I, CITY_G]

    def construct_building(self):
        if self.is_valid and self.game.stats.is_enough_resources(self.cost):
            self.construction_calculations(Construction(self.game, self.rect.x + (self.size[0] / 2) + self.game.camera.x,
                                                        self.rect.y + (self.size[1] / 2) + self.game.camera.y))

    def check_valid(self):
        """Cannot overlap with anything in order for it to build."""
        self.collision_detection(pg.sprite.spritecollide(self, self.game.collision_sprites, False), 1)


class WallGhost(Ghost):
    """Finally, it's done. Not yet, it's going to get ugly."""
    def __init__(self, game):
        super().__init__(game)
        self.child_init(WALL_VALID, WALL_INVALID)
        self.cost = [WALL_F, WALL_I, WALL_G]
        self.radius = WALL_MIN_BOOM
        self.collided_circle = []

    def construct_building(self):
        """Needs to also factor in plate cost. Ignore for now."""
        self.cost = [WALL_F, WALL_I, WALL_G]
        if self.game.ghost_plate:
            for plate in self.game.ghost_plate:
                self.cost[0] += WALL_F
                self.cost[1] += WALL_I
                self.cost[2] += WALL_G
            if self.is_valid and self.game.stats.is_enough_resources(self.cost):
                self.construction_calculations2(WallBuilding(self.game))
                for plate in self.game.ghost_plate:
                    plate.spawn_plate()
        else:
            if self.is_valid and self.game.stats.is_enough_resources(self.cost):
                self.construction_calculations2(WallBuilding(self.game))

    def construction_calculations2(self, building, *proxy_cost):
        self.game.stats.subtract_resources(self.cost)

    def check_valid(self):
        """Can overlap the map, other buildings, and itself. Has minimum distance necessary from other walls"""
        # Something about collision with city territory circle. If mouse cursor over city territory, print something

        self.radius = WALL_CIRCLE_RESTRICT
        self.collision_detection(pg.sprite.spritecollide(self.game.mouse, self.game.collision_sprites, False),
                                 pg.sprite.spritecollide(self.game.mouse, self.game.cities, False, collided=self.game.circol),
                                 pg.sprite.spritecollide(self, self.game.walls, False, collided=self.game.circol))

    def draw_circle(self):
        """Creates circle around ghost wall sprite. Active during debugging."""
        if self.collided_circle:
            pg.draw.circle(self.game.screen, THECOLORS['lightyellow1'],
                           ((self.rect.center[0] + self.game.camera.x), (self.rect.center[1] + self.game.camera.y)),
                           self.radius, 1)

    def child_update(self):
        """This fires every frame. Creates a circle boom and either spawns or deletes plates."""
        if not self.game.is_shift_pressed:
            self.circle_boom()
            if self.collided_circle:
                self.activate_runner()
            if not self.collided_circle:
                self.game.delete_ghost_plates()


    def circle_boom(self):
        """A circle grows in size until it collides with walls. Also has min radius from other walls."""
        self.collided_circle = None
        self.radius = WALL_MIN_BOOM
        while self.radius < WALL_MAX_BOOM:
            if not self.collided_circle:
                self.radius += WALL_ITERATION_BOOM
                self.collided_circle = pg.sprite.spritecollide(self, self.game.walls, False, collided=self.game.circol)
            else:
                break

    def activate_runner(self):
        """Tells the runner to spawn ghost plates while running to every wall in our self.collided_circle"""
        self.game.delete_ghost_plates()
        self.game.pass_length = len(self.collided_circle)
        for num, wall in enumerate(self.collided_circle, start=1):
            if self.game.is_alt_pressed and self.game.random_number != num:
                continue
            self.game.runner.run(self.rect.centerx, self.rect.centery, wall.rect.centerx, wall.rect.centery)


class PlateGhost(Ghost):
    def __init__(self, game, runner):
        super().__init__(game)
        self.runner = runner
        self.game.ghost_plate.add(self)
        self.game.current_run.add(self)
        self.cost = [WALL_F, WALL_I, WALL_G]
        self.colorkey = None
        # Rotation
        self.child_init()
        # Image information
        self.rect = self.image.get_rect()
        self.rect.centerx = self.runner.rect.centerx
        self.rect.centery = self.runner.rect.centery
        self.size = self.image.get_rect().size
        self.image.set_alpha(80)

    def child_init(self, *blank):
        """We calculate rotation, rotate the image, redefine rect, hide black filler, and make transparent."""
        # Check to see if wall is valid first, if that's not valid then plates are not valid.
        for wall in self.game.ghost_building:
            self.is_valid = wall.is_valid

        # I split rotating the image it into two statements for better image accuracy placement.
        rotate = math.degrees(math.atan2((self.runner.start_x - self.runner.move_x),
                                         (self.runner.start_y - self.runner.move_y)))
        if -1 <= self.runner.move_slope <= 1:
            if self.is_valid:
                self.image = pg.image.load(PLATE_HORIZONTAL_VALID)
            else:
                self.image = pg.image.load(PLATE_HORIZONTAL_INVALID)
            self.image = pg.transform.rotate(self.image.convert(), rotate - 90)
        else:
            if self.is_valid:
                self.image = pg.image.load(PLATE_VERTICAL_VALID)
            else:
                self.image = pg.image.load(PLATE_VERTICAL_INVALID)
            self.image = pg.transform.rotate(self.image.convert(), rotate)
        # Hides the black-filler from the rotation. If infinite slope, we skip.
        if rotate != 180 and rotate != 0:
            self.colorkey = self.image.get_at((0, 0))
            self.image.set_colorkey(self.colorkey)

    def spawn_plate(self):
        PlateBuilding(self.game, self.image, self.rect, self.size)


class TowerGhost(Ghost):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(TOWER_VALID, TOWER_INVALID)
        self.cost = [TOWER_F, TOWER_I, TOWER_G]
        self.colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(self.colorkey)

    def construct_building(self):
        if self.is_valid and self.game.stats.is_enough_resources(self.cost):
            self.construction_calculations(TowerBuilding(self.game))

    def check_valid(self):
        """Should be strict. Can overlap the map, other buildings, but not itself."""
        # wtf is this
        collision1 = pg.sprite.spritecollide(self, self.game.towers, False)
        collision1 += pg.sprite.spritecollide(self.game.mouse, self.game.collision_sprites, False)
        collision1 += pg.sprite.spritecollide(self, self.game.map_walls, False)
        self.collision_detection(collision1,
                                 pg.sprite.spritecollide(self.game.mouse, self.game.cities, False, collided=self.game.circol))

    def hide_color_key(self):
        self.colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(self.colorkey)


class KnightGhost(Ghost):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(KNIGHT_VALID, KNIGHT_INVALID)
        self.cost = [KNIGHT_F, KNIGHT_I, KNIGHT_G]
        self.rect = pg.Rect(1, 1, 1, 1)

    def construct_building(self):
        if self.is_valid and self.game.stats.is_enough_resources(self.cost):
            self.construction_calculations(Knight(self.game))

    def check_valid(self):
        """Should be not strict. Can overlap the map, other buildings, and itself."""
        self.collision_detection(pg.sprite.spritecollide(self.game.mouse, self.game.collision_sprites, False),
                                 pg.sprite.spritecollide(self.game.mouse, self.game.cities, False, collided=self.game.circol))
