# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
NEARBLACK = (20, 20, 20)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Main Settings
SCREEN_WIDTH = 1700
SCREEN_HEIGHT = 900
FPS = 100
GAME_TITLE = "Python RTS"
BGCOLOR = DARKGREY
WAIT_TIME = 2
CAMERA_SPEED_DEFAULT = 20  # 4
CAMERA_SPEED_FAST = 60  # 8
WINNING_CONDITION = 1000
NO_SURFACE = (0, 0)
NO_RECT = (0, 0, 0, 0)
PIXEL_RECT = (0, 0, 1, 1)
TRANSPARENCY = 80
BOX_TRANSPARENCY = 160
RESOURCE_TICK = .00111
RUNNER = 'images/runner.bmp'
# Resource Tick Timers: .002 (5.55 seconds) / .00111 (9.89 seconds) / .015 (7.38 seconds)

# Map Settings
TILESIZE = 150
GRIDWIDTH = SCREEN_WIDTH / TILESIZE
GRIDHEIGHT = SCREEN_HEIGHT / TILESIZE
MAPNAME = 'maps/map5.txt'

# Blank Settings (for parent classes)
UNIT_DESELECTED = 'images/BLANK_deselected.bmp'
BLANK_BUTTON = 'images/BLANK_Button.bmp'
BLANK_BUILDING = 'images/BLANK_Building.bmp'  # 150px by 150px

# =============================================== Units Settings ================================================== #

MAX_UNIT_SELECTION = 50
MAX_HOTKEY_SELECTION = 50
MAX_UNIT_CAP = 50
MIN_UNIT_CAP = 3

# Knight Settings (36px by 36px)
KNIGHT_DESELECTED = 'images/knight_deselected.bmp'
KNIGHT_SELECTED = 'images/knight_selected.bmp'
KNIGHT_SPEED = 1
KNIGHT_BUMP = 2

ENEMY_KNIGHT = 'images/enemy_knight.bmp'
ENEMY_KNIGHT_HP = 10

# =============================================== Button Settings ================================================== #

# Panel Settings
PANEL_WIDTH = 250
PANEL_HEIGHT = 30
PANEL_BUFFER = 10

# Building Button Settings
BUTTON_BUFFER = 5
CITY_BUTTON_DESELECTED = 'images/city_button_deselected.bmp'
WALL_BUTTON_DESELECTED = 'images/wall_button_deselected.bmp'
TOWER_BUTTON_DESELECTED = 'images/tower_button_deselected.bmp'
KNIGHT_BUTTON_DESELECTED = 'images/knight_button_deselected.bmp'

CITY_BUTTON_SELECTED = 'images/city_button_selected.bmp'
WALL_BUTTON_SELECTED = 'images/wall_button_selected.bmp'
TOWER_BUTTON_SELECTED = 'images/tower_button_selected.bmp'
KNIGHT_BUTTON_SELECTED = 'images/knight_button_selected.bmp'

# =============================================== Building Settings ================================================== #

DEBUG = False

# City Building
CITY_VALID = 'images/city_building.bmp'  # 150px by 150px
CITY_INVALID = 'images/city_building_invalid.bmp'
CITY_F = 40
CITY_I = 40
CITY_G = 32
CITY_F_R = -20
CITY_I_R = -20
CITY_G_R = -0
CITY_SUPPLY = 1
TRANSPARENT = (255, 255, 255)
TERRITORY_SHADE = 35
CITY_MAX_RADIUS = 300
CITY_START_RADIUS = 40
CONSTRUCT_TIME = .1

# Wall Building
WALL_VALID = 'images/wall_building.bmp'  # 66px by 66px
WALL_INVALID = 'images/wall_building_invalid.bmp'
WALL_F = 2
WALL_I = 3
WALL_G = .5
WALL_F_R = -1
WALL_I_R = -1.5
WALL_G_R = -0
WALL_SUPPLY = 0

# Wall Plate Logic
PLATE_HORIZONTAL_VALID = 'images/plate_horizontal_valid.bmp'  # 66 long, 33 tall
PLATE_VERTICAL_VALID = 'images/plate_vertical_valid.bmp'
PLATE_HORIZONTAL_INVALID = 'images/plate_horizontal_invalid.bmp'  # 66 long, 33 tall
PLATE_VERTICAL_INVALID = 'images/plate_vertical_invalid.bmp'
# Uses same resources and refunding as wall.

RUNNER_SPEED = 1
RUNNER_RADIUS = 65
RUNNER_BUFFER = 3
WALL_ITERATION_BOOM = 30
WALL_MAX_BOOM = 360
WALL_MIN_BOOM = 50
WALL_CIRCLE_RESTRICT = 80

# Tower Building
TOWER_VALID = 'images/tower_building.bmp'  # 66px by 66px
TOWER_INVALID = 'images/tower_building_invalid.bmp'
TOWER_F = 6
TOWER_I = 9
TOWER_G = 2
TOWER_F_R = -6
TOWER_I_R = -9
TOWER_G_R = -0
TOWER_SUPPLY = 0
TOWER_ARROW = 'images/tower_arrow.bmp'
TOWER_RADIUS = 300
TOWER_ARROW_SPEED = 5
TOWER_ARROW_DAMAGE = 4
TOWER_SHOOT_LIKELIHOOD = 500  # Since FPS is 100, an arrow will be shot once every 5 seconds on average.)
TOWER_ARROW_EXTRA_OVERLAP = 2

# Knight
KNIGHT_VALID = 'images/knight_deselected.bmp'  # forgot
KNIGHT_INVALID = 'images/knight_invalid.bmp'
KNIGHT_F = 9
KNIGHT_I = 6
KNIGHT_G = 0
KNIGHT_SUPPLY = 1
KNIGHT_HP = 10

# House Building? This increases supply

# =============================================== Resource Settings ================================================== #

# Starting Storage
FOOD_START = 300  # 120
IRON_START = 300  # 75
GOLD_START = 900  # 70
CREED_START = 0

# Starting Income (should only be after city is built or below minimum city requirements)
FOOD_INCOME = 8
IRON_INCOME = 8
GOLD_INCOME = 0

