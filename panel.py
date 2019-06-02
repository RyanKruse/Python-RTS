import pygame as pg
import pygame.font
from settings import *


class Panel:
    def __init__(self, game):
        """Initialize the game stats panel on top left."""
        self.game = game
        self.game.panels.append(self)

        # Size, color, and font information.
        self.width = PANEL_WIDTH
        self.height = PANEL_HEIGHT
        self.button_color = NEARBLACK
        self.text_color = WHITE
        self.font = pygame.font.SysFont(None, 32, True)

        # Image information.
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.width/2 + PANEL_BUFFER, self.height/2 + PANEL_BUFFER)
        self.msg = 'Blank'
        self.build_panel(self.msg)

    def draw_panel(self):
        """This gets called every frame. Draws screen first, then draws message over it."""
        self.game.screen.fill(self.button_color, self.rect)
        self.game.screen.blit(self.msg_image, self.msg_image_rect)

    def build_panel(self, msg):
        """Builds image using all initialized variables. Gets called by child class frequently."""
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def get_clicked(self):
        """Checks if we clicked on a button while CTRL is pressed."""
        if self.game.is_ctrl_pressed and self.game.is_ghost_building:
            return self.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
        else:
            return False


# =============================================== Child Classes ================================================== #
# The child panels track current resources, income, cities, units, and unit caps.

class FoodPanel(Panel):
    def __init__(self, game):
        super(FoodPanel, self).__init__(game)
        self.refresh_panel()

    def refresh_panel(self):
        self.build_panel('Food: ' + str(round(self.game.stats.food_stored)) + ' (+' + str(self.game.stats.food_income) + ')')


class IronPanel(Panel):
    def __init__(self, game):
        super(IronPanel, self).__init__(game)
        self.rect.y += PANEL_HEIGHT
        self.refresh_panel()

    def refresh_panel(self):
        self.build_panel('Iron: ' + str(round(self.game.stats.iron_stored)) + ' (+' + str(self.game.stats.iron_income) + ')')


class GoldPanel(Panel):
    def __init__(self, game):
        super(GoldPanel, self).__init__(game)
        self.rect.y += PANEL_HEIGHT * 2
        self.refresh_panel()

    def refresh_panel(self):
        self.build_panel('Gold: ' + str(round(self.game.stats.gold_stored)) + ' / ' + str(WINNING_CONDITION))


class CityPanel(Panel):
    def __init__(self, game):
        super(CityPanel, self).__init__(game)
        self.rect.y += PANEL_HEIGHT * 3
        self.refresh_panel()

    def refresh_panel(self):
        self.build_panel('Cities: ' + str(len(self.game.cities)))


class UnitPanel(Panel):
    def __init__(self, game):
        super(UnitPanel, self).__init__(game)
        self.rect.y += PANEL_HEIGHT * 4
        self.refresh_panel()

    def refresh_panel(self):
        self.build_panel('Supply: ' + str(len(self.game.units)) + ' / ' + str(MAX_UNIT_CAP))

