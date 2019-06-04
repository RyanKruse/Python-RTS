# Scroll-map Imports
import sys
import pygame as pg
import window
import game
from os import path
from pygame.sprite import Group
from settings import *
from sprites import Player, Wall

# My Imports
from unit import *
from ghost import *
from enemy import *
from hotkey import HotKey
from construction import *
from runner import Runner
from pygame.math import Vector2

# Due to frequency of use, Main = m, Group = g, Pygame = pg.


class Main:
    def __init__(self):
        # Initialize game.
        pg.init()
        pg.display.set_caption(GAME_TITLE)  # Program title
        self.g = game.Groups()
        self.resource = game.Resource(self)

        # Initialize window.
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.map = window.Map()
        self.camera = window.Camera(self)
        self.clock = window.Clock()
        self.mouse = window.Mouse(self)
        self.city_button = window.CityButton(self)
        self.wall_button = window.WallButton(self)
        self.tower_button = window.TowerButton(self)
        self.knight_button = window.KnightButton(self)
        self.food_panel = window.FoodPanel(self)
        self.iron_panel = window.IronPanel(self)
        self.gold_panel = window.GoldPanel(self)
        self.city_panel = window.CityPanel(self)
        self.unit_panel = window.UnitPanel(self)

        # Initialize menu buttons & logic
        self.is_ctrl_pressed = False
        self.is_shift_pressed = False
        self.is_alt_pressed = False
        self.is_ghost_building = False
        self.is_debugging = False
        self.mouse1_gate = False
        self.pass_length = 0
        self.random_number = 0

        # Initialize other code
        self.hotkey = HotKey(self)
        self.runner = Runner(self)

    def alive(self):
        return len(self.g.cities) > 0

    def new(self):
        """Initialize the map string for a new game. Creates walls and player (which camera follows)."""
        for row, tiles in enumerate(self.map.contents):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'i':
                    Iron(self, col, row)

    def run(self):
        while True:
            self.events()
            self.update()
            self.draw()

    # ================================================= User Events ================================================ #
    def events(self):
        """Catches all events here and calls appropriate function."""
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                self.key_down(event)
            elif event.type == pg.KEYUP:
                self.key_up(event)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_down(event)
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_up(event)
            elif event.type == pg.MOUSEMOTION:
                self.mouse_move(event)
            elif event.type == pg.QUIT:
                self.exit_game()

    def key_down(self, event):
        # C
        if event.key == pg.K_c:
            EnemyKnight(self)
            self.resource.refresh()
        # R & CTRL+R
        elif event.key == pg.K_r:
            if self.is_ctrl_pressed and self.is_ghost_building:
                self.destroy_ghost()
            elif self.g.selected_units:
                self.deselect_units()
            elif self.is_ctrl_pressed:
                self.refund_building()
        # SHIFT
        elif event.key == pg.K_LSHIFT:
            self.is_shift_pressed = True
            self.delete_ghost_plates()
            self.camera.speed = CAMERA_SPEED_FAST
        # CTRL
        elif event.key == pg.K_LCTRL:
            self.hide_ghost(True)
        # ALT
        elif event.key == pg.K_LALT:
            pass  # Currently crashes game.
            # self.is_alt_pressed = True
            # self.random_number = random.randint(1, self.pass_length)
        # Quit
        elif event.key == pg.K_ESCAPE:
            self.exit_game()
        # Q
        elif event.key == pg.K_q:
            self.is_debugging = not self.is_debugging
        # 1-9
        else:
            self.hotkey.check_events(event)

    def key_up(self, event):
        # SHIFT
        if event.key == pg.K_LSHIFT:
            self.is_shift_pressed = False
            self.camera.speed = CAMERA_SPEED_DEFAULT
        # CTRL
        elif event.key == pg.K_LCTRL:
            self.hide_ghost(False)
        # ALT
        elif event.key == pg.K_LALT:
            self.is_alt_pressed = False

    def mouse_down(self, event):
        # Construct building, construct ghost, or select units.
        if event.button == 1:
            self.mouse1_gate = True
            self.construct_building()
            self.construct_ghost()
            self.mouse.select_start()
        # Destroys ghost or commands units.
        elif event.button == 3:
            if self.is_ctrl_pressed and self.is_ghost_building:
                self.destroy_ghost()
            else:
                self.command_units()

    def mouse_up(self, event):
        # Finishes box selection.
        if event.button == 1:
            self.mouse1_gate = False
            self.mouse.select_finish()
        # Stops commanding
        elif event.button == 3:
            self.mouse.is_commanding = False

    def mouse_move(self, event):
        pass
    # ================================================ Main Functions =============================================== #

    def exit_game(self):
        """Quits game."""
        pg.quit()
        sys.exit()

    def deselect_units(self):
        """Deselects all units."""
        for unit in self.g.selected_units:
            unit.set_deselected()

    def destroy_ghost(self):
        """Destroys ghost and deselects all buttons."""
        for ghost in self.g.ghost_building:
            ghost.delete()
        for button in self.g.all_buttons:
            button.image = button.image_deselected
            button.selected = False
        self.is_ghost_building = False
        self.delete_ghost_plates()

    def hide_ghost(self, is_ctrl_pressed):
        """Adds or hides ghost from view."""
        self.is_ctrl_pressed = is_ctrl_pressed
        if self.is_ctrl_pressed:
            for ghost in self.g.ghost_building:
                self.g.all_sprites.add(ghost)
                self.is_ghost_building = True
        else:
            for ghost in self.g.ghost_building:
                self.g.all_sprites.remove(ghost)
                self.is_ghost_building = False
                self.delete_ghost_plates()

    def construct_building(self):
        """Construct building if ghost is selected."""
        if self.is_ctrl_pressed and self.is_ghost_building:
            gate = True
            # Allows construction only if not clicking on button or panel.
            for button in self.g.all_buttons:
                if button.is_clicked():
                    gate = False
            for panel in self.g.panels:
                if panel.is_clicked():
                    gate = False
            if gate:
                for ghost in self.g.ghost_building:
                    ghost.construct_building()

    def construct_ghost(self):
        """Creates building ghost when button is clicked."""
        for button in self.g.all_buttons:
            button.click()

    def command_units(self):
        """Defines move_x and move_y for selected units."""
        self.mouse.is_commanding = True
        for unit in self.g.selected_units:
            unit.set_move_location()

    def refund_building(self):
        """Refund building mouse hovering over."""
        mouse_collided = pg.sprite.spritecollide(self.mouse, self.g.buildings, False)
        if mouse_collided:
            refund_amount = mouse_collided[0].refund_amount
            mouse_collided[0].delete()
            self.resource.deduct(refund_amount)
            mouse_collided[0].delete()
        self.resource.refresh()

    def delete_ghost_plates(self):
        """Delete all ghost plates."""
        for plate in self.g.ghost_plate:
            pg.sprite.spritecollide(plate, self.g.ghost_plate, True)

    def circol(self, left, right):
        """Detects circle collision."""
        if left != right:
            distance = Vector2(left.rect.center).distance_to(right.rect.center)
            return distance < left.radius
        else:
            return False

    def arrived_at_location(self, obj):
        """Detects if sprite has arrived at move_x and move_y."""
        return (obj.move_x - obj.buffer <= obj.rect.centerx <= obj.move_x + obj.buffer) and \
               (obj.move_y - obj.buffer <= obj.rect.centery <= obj.move_y + obj.buffer)

    def slope_movement_logic(self, obj):
        """Defines slope and which quadrant sprite is moving towards."""
        # Figures out what our slope is. This makes the runner smoother when calculated every loop.
        if not obj.move_x - obj.rect.centerx == 0:
            obj.move_slope = (obj.move_y - obj.rect.centery) / (obj.move_x - obj.rect.centerx)

        # Checks to see what quadrant we'll move towards.
        if obj.rect.centerx < obj.move_x:
            # Quadrant 4
            if obj.rect.centery < obj.move_y:
                self.move_finite_slope(obj.speed, obj.move_slope, obj.speed, obj)
            # Quadrant 1
            else:
                self.move_finite_slope(obj.speed, -obj.move_slope, -obj.speed, obj)
        elif obj.rect.centerx > obj.move_x:
            # Quadrant 3
            if obj.rect.centery < obj.move_y:
                self.move_finite_slope(-obj.speed, -obj.move_slope, obj.speed, obj)
            # Quadrant 2
            else:
                self.move_finite_slope(-obj.speed, obj.move_slope, -obj.speed, obj)
        else:
            # Quadrant 5
            if obj.rect.centery < obj.move_y:
                self.move_infinite_slope(obj.move_y, obj.rect.centery, obj.speed, obj)
            # Quadrant 6
            elif obj.rect.centery > obj.move_y:
                self.move_infinite_slope(obj.rect.centery, obj.move_y, -obj.speed, obj)

    def move_finite_slope(self, s1, s2, s3, obj):
        """An algorithm to increase or decrease rect.x and rect.y."""
        if obj.move_counter < 1:
            obj.rect.x += s1
            obj.move_counter += s2
        else:
            obj.rect.y += s3
            obj.move_counter -= 1

    def move_infinite_slope(self, y1, y2, s1, obj):
        """An algorithm to increase or decrease rect.y only."""
        if y1 > y2:
            obj.rect.y += s1

    def collision_bump(self, obj, other):
        """This code is costly and doesn't work well with corner collision."""
        if other.rect.centerx == obj.rect.centerx or other.rect.centery == obj.rect.centery:
            # When units bump into each other, bumps diagonally. Prevents units from clumping over each other.
            if other.rect.centerx > obj.rect.centerx:
                obj.rect.x -= KNIGHT_SPEED
            elif other.rect.centerx < obj.rect.centerx:
                obj.rect.x += KNIGHT_SPEED
            if other.rect.centery > obj.rect.centery:
                obj.rect.y -= KNIGHT_SPEED
            elif other.rect.centery < obj.rect.centery:
                obj.rect.y += KNIGHT_SPEED
        else:
            # When units bump into each other, bumps diagonally, horizontally, or vertically.
            if other.rect.centerx < obj.rect.x + obj.size[0]:
                obj.rect.x += KNIGHT_SPEED
            if other.rect.centerx > obj.rect.x:
                obj.rect.x -= KNIGHT_SPEED
            if other.rect.centery < obj.rect.y + obj.size[1]:
                obj.rect.y += KNIGHT_SPEED
            if other.rect.centery > obj.rect.y:
                obj.rect.y -= KNIGHT_SPEED

    # =============================================== Clock & Update =============================================== #

    def update(self):
        """Updates clock, all sprites, camera, and resources."""
        self.update_clock()
        self.g.all_sprites.update()
        self.camera.update(self.player)
        self.resource.income()

    def update_clock(self):
        """Updates all the time variables in the game."""
        self.clock.delta_time = self.clock.clock.tick(FPS) / 1000
        self.clock.irl_time += self.clock.delta_time
        self.clock.resource_time += RESOURCE_TICK

    # ==================================================== Draw ==================================================== #

    def draw(self):
        """This draws everything onto screen."""
        # Draws first --> last
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.draw_circles()
        self.draw_ghost_plates()
        for sprite in self.g.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.draw_resources()
        self.draw_gui()
        pg.display.flip()

    def draw_grid(self):
        """Draws the grid locked to map. Tile size multiplied to reduce clutter."""
        for x in range(-self.player.rect[0], SCREEN_WIDTH, int(TILESIZE/2)):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(-self.player.rect[1], SCREEN_HEIGHT, int(TILESIZE/2)):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (SCREEN_WIDTH, y))

    def draw_gui(self):
        """This draws the GUI."""
        for panel in self.g.panels:
            panel.draw_panel()
        if self.is_ctrl_pressed:
            for button in self.g.all_buttons:
                if not button.restricted or self.alive():
                    self.screen.blit(button.image, button.rect)

    def draw_circles(self):
        """Draws circular territory and borders."""
        if self.is_debugging:
            if self.is_ctrl_pressed:
                for ghost in self.g.ghost_building:
                    ghost.draw_circle()
            for construction in self.g.construction:
                construction.draw_circle()
            for city in self.g.cities:
                mouse_collide = pg.sprite.spritecollide(city, self.g.mouse_group, False, collided=self.circol)
                if mouse_collide:
                    city.draw_territory()
        for city in self.g.cities:
            city.draw_circle()

    def draw_resources(self):
        """Draws the map food and iron."""
        for iron in self.g.map_iron:
            iron.draw()
        for food in self.g.map_food:
            food.draw()

    def draw_ghost_plates(self):
        """Draws our wall plates."""
        for plate in self.g.ghost_plate:
            self.screen.blit(plate.image, self.camera.apply(plate))
        for plate in self.g.plates:
            self.screen.blit(plate.image, self.camera.apply(plate))


# Creates and runs game class.
game = Main()
game.new()
game.run()
