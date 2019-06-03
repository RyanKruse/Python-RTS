import pygame as pg
from settings import *
from ghost import *
from os import path


class Map:
    """The map class sets up and contains the game map."""
    def __init__(self):
        # Open file and append string contents.
        self.name = path.join(path.dirname(__file__), MAPNAME)
        self.contents = []
        with open(self.name, 'rt') as file:
            for line in file:
                self.contents.append(line.strip())
        # Count columns as width. Count rows as height.
        self.count_width = len(self.contents[0])
        self.count_height = len(self.contents)
        self.pixel_width = self.count_width * TILESIZE
        self.pixel_height = self.count_height * TILESIZE


class Camera:
    """The camera class contains screen location data."""
    def __init__(self, main):
        # Create camera rects.
        self.camera = pg.Rect(0, 0, main.map.pixel_width, main.map.pixel_height)
        self.pixel_width = main.map.pixel_width
        self.pixel_height = main.map.pixel_height
        # Set camera speed and location.
        self.speed = CAMERA_SPEED_DEFAULT
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        self.x = -target.rect.x + int(SCREEN_WIDTH / 2)
        self.y = -target.rect.y + int(SCREEN_HEIGHT / 2)
        self.camera = pg.Rect(self.x, self.y, self.pixel_width, self.pixel_height)


class Clock:
    """The clock class contains game time."""
    def __init__(self):
        # Create clock and time variables.
        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.irl_time = 0
        self.resource_time = 0


# =============================================== Button Classes ================================================== #

class Button(pg.sprite.Sprite):
    def __init__(self, game):
        """Initialize the building buttons on bottom left."""
        self.groups = game.g.all_buttons
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # Image information
        self.image_deselected = pg.image.load(BLANK_BUTTON)
        self.image_selected = pg.image.load(BLANK_BUTTON)
        self.image = self.image_deselected
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        self.rect.x = BUTTON_BUFFER
        self.rect.y = SCREEN_HEIGHT - self.size[1] - BUTTON_BUFFER
        self.is_restricted = True
        self.is_selected = False

    def child_init(self, image_deselected, image_selected, restricted=True):
        """Child class initializations."""
        self.image_deselected = pg.image.load(image_deselected)
        self.image_selected = pg.image.load(image_selected)
        self.image = self.image_deselected
        self.size = self.image.get_rect().size
        self.is_restricted = restricted

    def is_clicked(self):
        """If mouse clicked on the menu button, deletes current ghost and creates ghost."""
        if self.get_clicked():
            if self.game.is_ghost_building:
                self.game.destroy_ghost()
            self.spawn_ghost()

    def get_clicked(self):
        """Checks if we clicked on a button while CTRL is pressed."""
        if self.game.is_ctrl_pressed and not self.is_restricted:
            return self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
        else:
            return False

    def get_restricted(self):
        """Checks to see if we have any cities. If not, this restricts the availability of all other buildings."""
        if not isinstance(self, CityButton):
            self.is_restricted = len(self.game.g.cities) == 0

    def deselect(self, ):
        if self.is_selected:
            self.is_selected = False
            self.image = self.image_deselected

    def set_selected(self):
        """Creates a highlighted button when clicked on."""
        for button in self.game.g.all_buttons:
            button.deselect()
        self.is_selected = True
        self.image = self.image_selected

    def spawn_ghost(self):
        """Creates a ghost of a building that follows the mouse cursor when button is clicked."""
        pass


class CityButton(Button):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(CITY_BUTTON_DESELECTED, CITY_BUTTON_SELECTED, False)
        self.rect.x = BUTTON_BUFFER

    def spawn_ghost(self):
        self.game.g.ghost_building.add(CityGhost(self.game))
        self.set_selected()


class WallButton(Button):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(WALL_BUTTON_DESELECTED, WALL_BUTTON_SELECTED)
        self.rect.x += self.game.city_button.rect.x + self.game.city_button.size[0]

    def spawn_ghost(self):
        self.game.g.ghost_building.add(WallGhost(self.game))
        self.set_selected()


class TowerButton(Button):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(TOWER_BUTTON_DESELECTED, TOWER_BUTTON_SELECTED)
        self.rect.x += self.game.wall_button.rect.x + self.game.wall_button.size[0]

    def spawn_ghost(self):
        self.game.g.ghost_building.add(TowerGhost(self.game))
        self.set_selected()


class KnightButton(Button):
    def __init__(self, game):
        super().__init__(game)
        self.child_init(KNIGHT_BUTTON_DESELECTED, KNIGHT_BUTTON_SELECTED)
        self.rect.x = SCREEN_WIDTH - self.size[0] - BUTTON_BUFFER

    def spawn_ghost(self):
        self.game.g.ghost_building.add(KnightGhost(self.game))
        self.set_selected()

