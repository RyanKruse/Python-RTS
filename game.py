import pygame as pg
from settings import *
from building import *
from unit import *
import math
from pygame.sprite import Sprite


class Groups:
    """The group class contains all pygame groups."""
    def __init__(self):
        # Draw-Collisions.
        self.all_sprites = pg.sprite.Group()
        self.collision_sprites = pg.sprite.Group()
        self.mouse_group = pg.sprite.Group()
        # Units.
        self.units = pg.sprite.Group()
        self.selected_units = pg.sprite.Group()
        self.enemy_units = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        # Ghosts.
        self.ghost_building = pg.sprite.Group()
        self.ghost_plate = pg.sprite.Group()
        self.current_run = pg.sprite.Group()
        # GUIs.
        self.all_buttons = pg.sprite.Group()
        self.panels = []
        # Maps.
        self.map_walls = pg.sprite.Group()
        self.map_iron = pg.sprite.Group()
        self.map_food = pg.sprite.Group()
        # Buildings.
        self.buildings = pg.sprite.Group()
        self.construction = pg.sprite.Group()
        self.cities = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.plates = pg.sprite.Group()
        self.towers = pg.sprite.Group()


class Resource:
    """The resource class tracks all resource statistics."""
    def __init__(self, main):
        self.main = main
        # Initialize starting resources.
        self.food = FOOD_START
        self.iron = IRON_START
        self.gold = GOLD_START
        self.creed = CREED_START
        # Initialize starting resource income.
        self.food_income = 0
        self.iron_income = 0
        self.gold_income = 0

    def income(self):
        """Add resources to storage for each resource tick."""
        if self.main.clock.resource_time >= 1:
            # Distribute resources and reset tick.
            self.food += self.food_income
            self.iron += self.iron_income
            self.gold += self.gold_income
            self.main.clock.resource_time = self.main.clock.resource_time - 1
            # Refresh and print statistics.
            print("%s food, %s iron, and %s gold has distributed at %s seconds."
                  % (self.food_income, self.iron_income, self.gold_income, round(self.main.clock.irl_time, 1)))
            self.refresh()

    def deduct(self, cost):
        """Subtract resources based on cost of object constructed."""
        self.food -= cost[0]
        self.iron -= cost[1]
        self.gold -= cost[2]
        self.refresh()

    def is_valid(self, cost):
        """Check if game has minimum resources to construct object."""
        return self.food >= cost[0] and self.iron >= cost[1] and self.gold >= cost[2]

    def refresh(self):
        """Refresh resource income and GUI panels."""
        # Standard update of income.
        if self.main.alive():
            self.food_income = FOOD_INCOME  # TODO: Configure income based on resource nodes captured.
            self.iron_income = IRON_INCOME  # TODO: Configure income based on resource nodes captured.
            self.gold_income = len(self.main.g.cities)
        else:
            self.food_income = 0
            self.iron_income = 0
            self.gold_income = 0
        # If no cities, provide enough income to build one city.
        if self.food < CITY_F and not self.main.alive():
            self.food_income = FOOD_INCOME
        if self.iron < CITY_I and not self.main.alive():
            self.iron_income = IRON_INCOME
        if self.gold < CITY_G and not self.main.alive():
            self.gold_income = GOLD_INCOME
        # Update GUI panels.
        for panel in self.main.g.panels:
            panel.refresh_panel()


class HotKey:  # TODO: Github code cleanup.
    def __init__(self, game):
        self.game = game
        self.hotkey_numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.hotkey_group = {}
        self.new_group()

    def new_group(self):
        """Creates the hotkey groups"""
        for number in self.hotkey_numbers:
            self.hotkey_group[number] = pg.sprite.Group()

    def get(self, num):
        """Gets a specific hotkey group."""
        return self.hotkey_group.get(num)

    def check_events(self, event):
        """Checks to see if we are utilizing hotkeys."""
        if self.game.is_ctrl_pressed and pg.key.name(event.key) in self.hotkey_numbers:
            self.add_unit_hotkey(pg.key.name(event.key))
        elif pg.key.name(event.key) in self.hotkey_numbers:
            self.select_hotkey(pg.key.name(event.key))

    def add_unit_hotkey(self, num):
        """Adds the units into the hotkey group."""
        self.get(num).empty()
        for unit in self.game.g.selected_units:
            if len(self.get(num)) < MAX_HOTKEY_SELECTION:
                pg.sprite.Group.add(self.get(num), unit)
        print(str(self.get(num)))

    def select_hotkey(self, num):
        """Selects the units in the hotkey group."""
        self.game.deselect_units()
        for unit in self.get(num):
            unit.select_button()  # TODO: Debug button knight class missing.


class Runner(Sprite):  # TODO: Github code cleanup.
    """This class runs from point A to point B and tried to spawn a building every frame of the way."""
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        # Image Information
        self.image = pg.image.load(RUNNER)
        self.size = self.image.get_rect().size
        self.rect = self.image.get_rect()
        # Movement slope information
        self.start_x = 0
        self.start_y = 0
        self.move_x = 0
        self.move_y = 0
        self.move_slope = 0
        self.move_quadrant = 0
        self.move_counter = 0
        # Spawn plate information
        self.radius = RUNNER_RADIUS
        self.speed = RUNNER_SPEED
        self.buffer = RUNNER_BUFFER
        self.collided_circle = None
        self.collided_ghosts = None
        self.is_running = False

    def run(self, start_x, start_y, move_x, move_y):
        """This makes the runner spawn plates."""
        self.reset_runner(start_x, start_y, move_x, move_y)
        while self.is_running:
            self.set_move_slope()
            self.collision_detection()

    def set_move_slope(self):
        """This calculates the movement slope and what quadrant our sprite is moving towards."""
        # Checks to see if we made it to the move location. Stops within general vicinity (buffer).
        if self.game.arrived_at_location(self):
            self.is_running = False
        self.game.slope_movement_logic(self)

    def collision_detection(self):
        """We spawn a ghost plate any time the runner is not colliding with a ghost plate or ghost wall."""
        self.collided_circle = pg.sprite.spritecollide(self, self.game.g.current_run, False, collided=self.game.circol)\
            + pg.sprite.spritecollide(self, self.game.g.ghost_building, False)
        if not self.collided_circle:
            PlateGhost(self.game, self)

    def reset_runner(self, start_x, start_y, move_x, move_y):
        """We reset the runner back to ghost-wall position and prepare it for multiple wall running"""
        self.is_running = True
        self.start_x = start_x
        self.start_y = start_y
        self.move_x = move_x
        self.move_y = move_y
        self.rect.centerx = start_x
        self.rect.centery = start_y
        self.game.g.current_run.empty()
        self.move_counter = 0
