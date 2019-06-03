import pygame as pg
from settings import *
from building import *


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
