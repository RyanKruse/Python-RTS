import pygame as pg
from pygame.sprite import Sprite
from settings import *
from pygame.math import Vector2
from pygame.color import THECOLORS
from unit import *
import math
import random

# Put this into the __init__ to see the effects.
# self.colorkey = self.image.get_at((0, 0)) - this can make the image transparent based on pixel!
# self.image.set_colorkey(self.colorkey)


# =============================================== Ghost Class ================================================== #
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
        self.game.g.all_sprites.add(self)
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
        pg.sprite.spritecollide(self, self.game.g.ghost_building, True)

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
        self.game.resource.deduct(self.cost)

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


class CityGhost(Ghost):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(CITY_VALID, CITY_INVALID)
        self.cost = [CITY_F, CITY_I, CITY_G]

    def construct_building(self):
        if self.is_valid and self.game.resource.is_valid(self.cost):
            self.construction_calculations(Construction(
                self.game, self.rect.x + (self.size[0] / 2) + self.game.camera.x,
                self.rect.y + (self.size[1] / 2) + self.game.camera.y))

    def check_valid(self):
        """Cannot overlap with anything in order for it to build."""
        self.collision_detection(pg.sprite.spritecollide(self, self.game.g.collision_sprites, False), 1)


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
        if self.game.g.ghost_plate:
            for plate in self.game.g.ghost_plate:
                self.cost[0] += WALL_F
                self.cost[1] += WALL_I
                self.cost[2] += WALL_G
            if self.is_valid and self.game.resource.is_valid(self.cost):
                self.construction_calculations2(WallBuilding(self.game))
                for plate in self.game.g.ghost_plate:
                    plate.spawn_plate()
        else:
            if self.is_valid and self.game.resource.is_valid(self.cost):
                self.construction_calculations2(WallBuilding(self.game))

    def construction_calculations2(self, building, *proxy_cost):
        self.game.resource.deduct(self.cost)

    def check_valid(self):
        """Can overlap the map, other buildings, and itself. Has minimum distance necessary from other walls"""
        # Something about collision with city territory circle. If mouse cursor over city territory, print something

        self.radius = WALL_CIRCLE_RESTRICT
        self.collision_detection(
            pg.sprite.spritecollide(self.game.mouse, self.game.g.collision_sprites, False),
            pg.sprite.spritecollide(self.game.mouse, self.game.g.cities, False, collided=self.game.circol),
            pg.sprite.spritecollide(self, self.game.g.walls, False, collided=self.game.circol))

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
                self.collided_circle = pg.sprite.spritecollide(
                    self, self.game.g.walls, False, collided=self.game.circol)
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
        self.game.g.ghost_plate.add(self)
        self.game.g.current_run.add(self)
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
        for wall in self.game.g.ghost_building:
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
        if self.is_valid and self.game.resource.is_valid(self.cost):
            self.construction_calculations(TowerBuilding(self.game))

    def check_valid(self):
        """Should be strict. Can overlap the map, other buildings, but not itself."""
        # wtf is this
        collision1 = pg.sprite.spritecollide(self, self.game.g.towers, False)
        collision1 += pg.sprite.spritecollide(self.game.mouse, self.game.g.collision_sprites, False)
        collision1 += pg.sprite.spritecollide(self, self.game.g.map_walls, False)
        self.collision_detection(
            collision1, pg.sprite.spritecollide(self.game.mouse, self.game.g.cities, False, collided=self.game.circol))

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
        if self.is_valid and self.game.resource.is_valid(self.cost):
            self.construction_calculations(Knight(self.game))

    def check_valid(self):
        """Should be not strict. Can overlap the map, other buildings, and itself."""
        self.collision_detection(
            pg.sprite.spritecollide(self.game.mouse, self.game.g.collision_sprites, False),
            pg.sprite.spritecollide(self.game.mouse, self.game.g.cities, False, collided=self.game.circol))


# ============================================= Construction Class ================================================ #
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
        pg.draw.circle(self.surf1, THECOLORS['lightcyan1'], (
            round((self.rect.center[0] + self.game.camera.x) + self.radius - x),
            round((self.rect.center[1] + self.game.camera.y) + self.radius - y)), self.radius)

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
            self.delete()


# =============================================== Building Class ================================================== #
class Building(Sprite):
    def __init__(self, game):
        self.groups = game.g.all_sprites, game.g.collision_sprites, game.g.buildings
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
        for ghost in self.game.g.ghost_building:
            self.rect.centerx = ghost.rect.centerx
            self.rect.centery = ghost.rect.centery
        self.cost = [food_cost, iron_cost, gold_cost]
        self.refund_amount = [food_refund, iron_refund, gold_refund]
        self.child_inits_specific()

    def delete(self):
        """Deletes self."""
        pg.sprite.spritecollide(self.game.mouse, self.game.g.buildings, True)

    def child_update(self):
        """Specific updates for child classes."""
        pass

    def child_inits_specific(self):
        """Specific inits for child classes."""
        pass

    def refund_resources(self):
        """Refunds resources based on child class."""
        pass


class CityBuilding(Building):
    def __init__(self, game, x, y, surf1):
        super().__init__(game)
        self.child_inits(CITY_VALID, CITY_F, CITY_I, CITY_G, CITY_F_R, CITY_I_R, CITY_G_R)
        pg.sprite.Group.add(self.game.g.cities, self)
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
        self.game.screen.blit(
            self.surf1, ((self.rect.center[0] + self.game.camera.x) - CITY_MAX_RADIUS,
                         (self.rect.center[1] + self.game.camera.y) - CITY_MAX_RADIUS, 0, 0))


class WallBuilding(Building):
    """Major experimenting. Do walls today."""
    def __init__(self, game):
        super().__init__(game)
        self.child_inits(WALL_VALID, WALL_F, WALL_I, WALL_G, WALL_F_R, WALL_I_R, WALL_G_R)
        pg.sprite.Group.add(self.game.g.walls, self)
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
            pg.draw.circle(
                self.game.screen, THECOLORS['lightcyan1'],
                ((collided.rect.center[0] + self.game.camera.x), (collided.rect.center[1] + self.game.camera.y)),
                collided.radius, 1)


class TowerBuilding(Building):
    def __init__(self, game):
        super().__init__(game)
        self.child_inits(TOWER_VALID, TOWER_F, TOWER_I, TOWER_G, TOWER_F_R, TOWER_I_R, TOWER_G_R)
        pg.sprite.Group.add(self.game.g.towers, self)
        pg.sprite.Group.remove(self.game.g.collision_sprites, self)
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
        self.enemies_in_range = pg.sprite.spritecollide(self, self.game.g.enemy_units, False, collided=self.game.circol)
        if self.enemies_in_range:
            for enemy in self.enemies_in_range:
                """We only want to shoot the first enemy"""
                if random.randint(1, TOWER_SHOOT_LIKELIHOOD) == 1:
                    TowerArrow(self.game, self.rect.centerx, self.rect.centery, enemy.rect.centerx, enemy.rect.centery,
                               self.game.g.enemy_units)
                break


class PlateBuilding(Building):
    def __init__(self, game, image, rect, size):
        super().__init__(game)
        pg.sprite.Group.add(self.game.g.plates, self)
        pg.sprite.Group.remove(self.game.g.all_sprites, self)
        self.child_inits(image, WALL_F, WALL_I, WALL_G, WALL_F_R, WALL_I_R, WALL_G_R)
        self.rect = rect
        self.size = size
        self.image.set_alpha(500)

    def child_inits(self, image, food_cost, iron_cost, gold_cost, food_refund, iron_refund, gold_refund):
        """Plates has its own child_inits because it is unqiue from other buildigns."""
        self.image = image
        self.cost = [food_cost, iron_cost, gold_cost]
        self.refund_amount = [food_refund, iron_refund, gold_refund]


class TowerArrow(Sprite):
    """This is an arrow projectile, spawned by tower. It can be used for friendly/foe."""
    def __init__(self, game, start_x, start_y, move_x, move_y, enemy_group):
        self.groups = game.g.all_sprites, game.g.projectiles
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
            pg.sprite.spritecollide(self, self.game.g.projectiles, True)
            if obj.health <= 0:
                obj.delete()
            break

    def overlap_decay(self):
        """If projectile misses its target, it flies extra until it decays."""
        self.overlap -= 1
        if self.overlap == 0:
            pg.sprite.spritecollide(self, self.game.g.projectiles, True)
        self.move_x = self.rect.x + (self.move_x - self.start_x)
        self.move_y = self.rect.y + (self.move_y - self.start_y)