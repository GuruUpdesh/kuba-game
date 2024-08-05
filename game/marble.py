import pygame
from .constants import SQUARE_SIZE, RED, WHITE, BLACK, BLUE, GREEN

class Marble:
    """
    Represents a marble in the board game Kuba.

    Parameters:
        row (integer 0-6): represents the current row of the marble
        col (integer 0-6): represents the current col of the marble

        ** If the marble is no longer on the board both variables will be assigned None **

        color (str "W", "B", or "R"):
            represents the color of the marble, white and back marbles are player marbles
            and red marbles are objective marbles

    The marble class is fairly rudimentary and simply functions as a representation of the marbles on the game board.
    This class communicates to the KubaGame class and provides information: position on the board (row, col) and color.

    The KubaGame class communicates back to this functions move method when a marbles position is changed. So that the
    row and col variables can be accurate for any state of the board.
    """

    def __init__(self, row, col, color):
        """
        Initializes private data members in the Marble class.

        row (integer 0-6): represents the current row of the marble
        col (integer 0-6): represents the current ccl of the marble

        ** If the marble is no longer on the board both variables will be assigned None **

        color (str "W", "B", or "R"):
            represents the color of the marble, white and back marbles are player marbles
            and red marbles are objective marbles
        """
        self._row = row
        self._col = col
        self._color = color


        ### pygame
        self.selected = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def __repr__(self):
        """
        Creates a representation for marble objects.
        """
        return str(self._color) + ' ' + str(self._row) + ',' + str(self._col)

    def get_row(self):
        """
        Gets the row of a marble object.
        Parameters:
            None
        Return:
            self._row
        """
        return self._row

    def get_col(self):
        """
        Gets the col of a marble object.
        Parameters:
            None
        Return:
            self._coll
        """
        return self._col

    def get_color(self):
        """
        Gets the color of a marble object.
        Parameters:
            None
        Return:
            self._color
        """
        return self._color

    def move(self, row_col):
        """
        Updates the position of a marble object.
        Parameters:
            row_col (tuple (row, col))
        """
        if row_col is None:
            self._row = None
            self._col = None
        else:
            row, col = row_col
            self._row = row
            self._col = col

    ### Pygame

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.get_col() + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.get_row() + SQUARE_SIZE // 2

    def draw(self, win, x, y, square_size):
        radius = square_size // 2 - 5
        
        if self._color == "R":
            base_color = RED
            gradient_color = (255, 150, 150)  # Lighter red
        elif self._color == "W":
            base_color = WHITE
            gradient_color = (220, 220, 220)  # Slightly darker white
        elif self._color == "B":
            base_color = BLACK
            gradient_color = (100, 100, 100)  # Lighter black

        # Draw selection circle
        if self.selected:
            pygame.draw.circle(win, GREEN, (int(x), int(y)), radius + 2)

        # Draw gradient
        for i in range(int(radius), 0, -1):
            ratio = i / radius
            color = [int(base_color[j] * ratio + gradient_color[j] * (1 - ratio)) for j in range(3)]
            pygame.draw.circle(win, color, (int(x), int(y)), i)

        # Add shine
        shine_radius = int(radius * 0.4)
        shine_offset = int(radius * -0.2)
        for i in range(shine_radius, 0, -1):
            alpha = int(255 * (1 - i / shine_radius))
            shine_color = (255, 255, 255, alpha)
            shine_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shine_surface, shine_color, (radius, radius), i)
            win.blit(shine_surface, (int(x - radius + shine_offset), int(y - radius + shine_offset)))
