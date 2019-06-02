from settings import *
from building import *


class Stats:
    def __init__(self, game):
        """Initialize resource/game statistics tracked."""
        self.game = game
        # Base storage of food, iron, gold, and creed.
        self.food_stored = FOOD_STORAGE
        self.iron_stored = IRON_STORAGE
        self.gold_stored = GOLD_STORAGE
        self.creed_stored = CREED_STORAGE
        # Base income of food, iron, and gold.
        self.food_income = 0
        self.iron_income = 0
        self.gold_income = len(self.game.cities)

    def update_resources(self):
        """Every resource tick we add resources to our storage."""
        if self.game.r_tick > 1 and len(self.game.cities) > 0:
            self.game.r_tick -= 1
            self.food_stored += self.food_income
            self.iron_stored += self.iron_income
            self.gold_stored += self.gold_income
            self.refresh_panels()
            print(str(self.food_income) + ' food, ' + str(self.iron_income) + ' iron, and ' + str(self.gold_income) +
                  ' gold has distrubted at ' + str(round(self.game.irl_seconds_played, 1)) + ' seconds.')

    def subtract_resources(self, cost):
        """Subtract resources from storage when building things."""
        self.food_stored -= cost[0]
        self.iron_stored -= cost[1]
        self.gold_stored -= cost[2]
        self.refresh_income()

    def is_enough_resources(self, cost):
        """Checks if we have minimum resources to build."""
        return self.food_stored >= cost[0] and self.iron_stored >= cost[1] and self.gold_stored >= cost[2]

    def refresh_panels(self):
        """Refreshes all panels."""
        for panel in self.game.panels:
            panel.refresh_panel()

    def refresh_income(self):
        """Refresh our current income."""
        if len(self.game.cities) > 0:
            self.food_income = FOOD_INCOME
            self.iron_income = IRON_INCOME
            self.gold_income = len(self.game.cities)
        else:
            self.food_income = 0
            self.iron_income = 0
            self.gold_income = 0
        self.refresh_panels()



