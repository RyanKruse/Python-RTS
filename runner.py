import pygame as pg
from pygame.sprite import Sprite
from settings import *
from sprites import *
from ghost import *
from construction import *
from unit import *
import math

class Runner(Sprite):
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

# =============================================== Runner Logic ================================================== #
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
