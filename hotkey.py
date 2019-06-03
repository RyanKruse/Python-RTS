import pygame as pg
from settings import *


class HotKey:
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
            unit.set_selected()
