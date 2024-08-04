# Board dimensions
WIDTH, HEIGHT = 1600, 900  # 16:9 aspect ratio
BOARD_SIZE = min(WIDTH, HEIGHT) * 0.8
ROWS, COLS = 7, 7
SQUARE_SIZE = WIDTH // COLS

# Colors
RED = (255, 0, 0)
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)
GREY_1 = (128, 128, 128)
GREY_2 = (169, 169, 169)
BLUE = (255, 255, 255)
GREEN = (0, 255, 0)
BACKGROUND = (240, 240, 240)

class Color:
    CGREY = '\33[90m'
    CRED = '\33[31m'
    CEND = '\33[0m'
    CBOLD = '\33[1m'
    CVIOLET = '\33[35m'

# Directions
LEFT = 'L'
RIGHT = 'R'
FORWARD = 'F'
BACKWARD = 'B'

# Player names
PLAYER_A = 'PA'
PLAYER_B = 'PB'