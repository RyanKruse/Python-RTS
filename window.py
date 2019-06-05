import pygame as pg
from settings import *
from os import path
from unit import Unit
import pygame.gfxdraw
import pygame.font
from pygame.color import THECOLORS
from building import *
import pygame.font


# ================================================ Essential Classes ================================================ #
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


class Mouse(pg.sprite.Sprite):  # TODO: Github code cleanup.
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

    def set_pos(self):
        """This tracks cursor position at all times not selecting units. Used for refunding building/units."""
        self.rect.x = pg.mouse.get_pos()[0] - self.game.camera.x
        self.rect.y = pg.mouse.get_pos()[1] - self.game.camera.y


class Player(pg.sprite.Sprite):  # TODO: Github code cleanup.
    def __init__(self, game, x, y):
        self.groups = game.g.all_sprites
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
            self.x -= self.game.camera.speed
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            self.x += self.game.camera.speed
        if keys[pygame.K_w] and not keys[pygame.K_s]:
            self.y -= self.game.camera.speed
        elif keys[pygame.K_s] and not keys[pygame.K_w]:
            self.y += self.game.camera.speed

    def update(self):
        self.get_keys()
        self.rect.x = self.x
        self.rect.y = self.y


class Wall(pg.sprite.Sprite):  # TODO: Github code cleanup.
    """I don't know what those game.x functions are."""
    def __init__(self, game, x, y):
        self.groups = game.g.all_sprites, game.g.collision_sprites, game.g.map_walls
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


class Iron(pg.sprite.Sprite):  # TODO: Github code cleanup.
    def __init__(self, game, x, y):
        self.groups = game.g.all_sprites, game.g.collision_sprites, game.g.map_iron
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE/2, TILESIZE/2), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = (x * TILESIZE + (TILESIZE / 4))
        self.rect.y = (y * TILESIZE + (TILESIZE / 4))

    def draw(self):
        pygame.gfxdraw.filled_circle(self.image, round(TILESIZE / 4), round(TILESIZE / 4),
                                     round(TILESIZE / 5), THECOLORS['gray'])


# =================================================== Button Class ================================================== #
class Button(pg.sprite.Sprite):
    """The button class is a sprite on the bottom that spawn ghost buildings when clicked."""
    def __init__(self, main, selected, deselected, ghost, restricted=True):
        pg.sprite.Sprite.__init__(self, main.g.all_buttons)
        self.main = main
        self.ghost = ghost  # String of spawned ghost building
        self.restricted = restricted  # Button appears if city >= 1
        # Calibrate button image.
        self.image_deselected = pg.image.load(deselected)
        self.image_selected = pg.image.load(selected)
        self.image = self.image_deselected
        # Calibrate button rects.
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        self.rect.x = BUTTON_BUFFER  # Overwritten by child
        self.rect.y = SCREEN_HEIGHT - self.size[1] - BUTTON_BUFFER

    def click(self):
        """Create ghost and select button if clicked."""
        if self.is_clicked():
            self.main.destroy_ghost()
            self.select_button()
            self.spawn_ghost()

    def is_clicked(self):
        """Return True if button rect is clicked; button sprite must be appearing."""
        if self.main.is_ctrl_pressed and (self.main.alive() or not self.restricted):
            return self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])

    def select_button(self):
        """Select button and deselect all other buttons."""
        for button in self.main.g.all_buttons:
            button.image = button.image_deselected
        self.image = self.image_selected

    def spawn_ghost(self):
        """Create ghost building that follows cursor."""
        exec('self.main.g.ghost_building.add(' + self.ghost + '(self.main))')


class CityButton(Button):
    def __init__(self, main):
        super().__init__(main, CITY_BUTTON_SELECTED, CITY_BUTTON_DESELECTED, 'CityGhost', False)
        self.rect.x = BUTTON_BUFFER  # Button appears 1st-left.


class WallButton(Button):
    def __init__(self, main):
        super().__init__(main, WALL_BUTTON_SELECTED, WALL_BUTTON_DESELECTED, 'WallGhost')
        self.rect.x += self.main.city_button.rect.x + self.main.city_button.size[0]  # Button appears 2nd-left.


class TowerButton(Button):
    def __init__(self, main):
        super().__init__(main, TOWER_BUTTON_SELECTED, TOWER_BUTTON_DESELECTED, 'TowerGhost')
        self.rect.x += self.main.wall_button.rect.x + self.main.wall_button.size[0]  # Button appears 3rd-left.


class KnightButton(Button):
    def __init__(self, main):
        super().__init__(main, KNIGHT_BUTTON_SELECTED, KNIGHT_BUTTON_DESELECTED, 'KnightGhost')
        self.rect.x = SCREEN_WIDTH - self.size[0] - BUTTON_BUFFER  # Button appears 1st-right.


# =================================================== Panel Class =================================================== #
class Panel:
    """The panel class is a widget on the top left that displays game data."""
    def __init__(self, main, slot):
        main.g.panels.append(self)
        self.main = main
        # Calibrate panel features.
        self.background_color = NEARBLACK
        self.text_color = WHITE
        self.text_font = pygame.font.SysFont(None, 32, True)
        # Calibrate panel rects.
        self.rect = pygame.Rect(0, 0, PANEL_WIDTH, PANEL_HEIGHT)
        self.rect.center = (PANEL_WIDTH/2 + PANEL_BUFFER, PANEL_HEIGHT/2 + PANEL_BUFFER)
        self.rect.y += PANEL_HEIGHT * slot
        self.refresh_panel()

    def draw_panel(self):
        """Draw panel background first then draw message over it."""
        self.main.screen.fill(self.background_color, self.rect)
        self.main.screen.blit(self.msg_image, self.msg_image_rect)

    def refresh_panel(self):
        """Convert panel message string to drawable image; re-center message rect."""
        self.msg_image = self.text_font.render(self.get_message(), True, self.text_color, self.background_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def is_clicked(self):
        """Return True if panel rect is clicked; prevents spawning buildings over panel."""
        if self.main.is_ctrl_pressed and self.main.is_ghost_building:
            return self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])

    def get_message(self):
        """Get the panel message from child class."""
        pass


class FoodPanel(Panel):
    def __init__(self, main):
        self.main = main
        super(FoodPanel, self).__init__(main, 0)

    def get_message(self):
        return 'Food: ' + str(round(self.main.resource.food)) + ' (+' + str(self.main.resource.food_income) + ')'


class IronPanel(Panel):
    def __init__(self, main):
        super(IronPanel, self).__init__(main, 1)

    def get_message(self):
        return 'Iron: ' + str(round(self.main.resource.iron)) + ' (+' + str(self.main.resource.iron_income) + ')'


class GoldPanel(Panel):
    def __init__(self, main):
        super(GoldPanel, self).__init__(main, 2)

    def get_message(self):
        return 'Gold: ' + str(round(self.main.resource.gold)) + ' / ' + str(WINNING_CONDITION)


class CityPanel(Panel):
    def __init__(self, main):
        super(CityPanel, self).__init__(main, 3)

    def get_message(self):
        return 'Cities: ' + str(len(self.main.g.cities))


class UnitPanel(Panel):
    def __init__(self, main):
        super(UnitPanel, self).__init__(main, 4)

    def get_message(self):
        return 'Supply: ' + str(len(self.main.g.units)) + ' / ' + str(MAX_UNIT_CAP)
