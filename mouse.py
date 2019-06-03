import pygame as pg
from settings import *
from unit import Unit


class Mouse(pg.sprite.Sprite):
    """The mouse class handles the selection box."""
    def __init__(self, game):
        self.groups = game.g.all_sprites, game.g.mouse_group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # Selection box information.
        self.is_selecting = False
        self.quadrant = 0
        self.lock_x = 0
        self.lock_y = 0
        self.moved_x = 0
        self.moved_y = 0

        # Image information.
        self.image = pg.Surface(NO_SURFACE)
        self.size = self.image.get_rect().size
        self.rect = pg.Rect(PIXEL_RECT)
        self.alpha_surface = None
        self.radius = CITY_MAX_RADIUS

        # Unit commander.
        self.is_commanding = False

    def update(self):
        """This fires every single frame."""
        if self.is_selecting and not self.game.is_ghost_building:
            self.build_box()
        else:
            self.set_pos()

# =============================================== Selection Box ================================================== #
    def select_start(self):
        """Sets variables necessary for selecting units. Opens gate in self.update to call build_box."""
        if not self.game.is_ghost_building:
            self.is_selecting = True
            self.lock_x = pg.mouse.get_pos()[0] - self.game.camera.x
            self.lock_y = pg.mouse.get_pos()[1] - self.game.camera.y
            self.rect.x = self.lock_x
            self.rect.y = self.lock_y

    def select_finish(self):
        """Sets the rect, gets collided sprites (units), adds to selected_units, and wipes all box data."""
        if not self.game.is_ghost_building:
            self.is_selecting = False
            self.rect = pg.Rect(self.rect.x, self.rect.y, self.image.get_rect().size[0], self.image.get_rect().size[1])
            collided = pg.sprite.spritecollide(self, self.game.g.units, False)
            self.image = pg.Surface(NO_SURFACE)
            self.rect = pg.Rect(PIXEL_RECT)

            # Lets units know they are selected. We don't want to select more than the max allowance.
            for unit in collided:
                if len(self.game.g.selected_units) >= MAX_UNIT_SELECTION:
                    break
                if isinstance(unit, Unit):
                    unit.set_selected()

    def build_box(self):
        """This builds a transparent selection box. Defines quadrant to call define_box."""
        self.moved_x = pg.mouse.get_pos()[0] - self.game.camera.x
        self.moved_y = pg.mouse.get_pos()[1] - self.game.camera.y

        # Figures out which quadrant we're in.
        if (0 < self.moved_x - self.lock_x) and (0 < self.moved_y - self.lock_y):
            self.define_box(4, self.lock_x, self.lock_y, self.moved_x, self.moved_y)
        elif (0 < self.moved_x - self.lock_x) and (0 > self.moved_y - self.lock_y):
            self.define_box(1, self.lock_x, self.moved_y, self.moved_x, self.lock_y)
        elif (0 > self.moved_x - self.lock_x) and (0 > self.moved_y - self.lock_y):
            self.define_box(2, self.moved_x, self.moved_y, self.lock_x, self.lock_y)
        elif (0 > self.moved_x - self.lock_x) and (0 < self.moved_y - self.lock_y):
            self.define_box(3, self.moved_x, self.lock_y, self.lock_x, self.moved_y)

        # Makes box transparent.
        self.image.set_alpha(BOX_TRANSPARENCY)

    def define_box(self, quadrant, rect_x, rect_y, base_x, base_y):
        """This creates the selection box. Box rect.x and rect.y always needs to be drawn from the top left corner."""
        self.quadrant = quadrant
        self.rect.x = rect_x
        self.rect.y = rect_y
        self.image = pg.Surface((base_x - self.rect.x, base_y - self.rect.y))
        self.image.fill(LIGHTGREY)

# =============================================== Other Logic ================================================== #
    def set_pos(self):
        """This tracks cursor position at all times not selecting units. Used for refunding building/units."""
        self.rect.x = pg.mouse.get_pos()[0] - self.game.camera.x
        self.rect.y = pg.mouse.get_pos()[1] - self.game.camera.y

