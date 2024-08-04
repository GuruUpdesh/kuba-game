import pygame
from .constants import Color, GREY_1, GREY_2, GREEN, ROWS, SQUARE_SIZE
from .marble import Marble

class KubaGame:
    """
        Represents the board game Kuba.

        Parameters:
            p1 (tuple (player1-name, marble-color))
                player1_name (str)
                marble-color (str "W", "B", or "R")
            p2 (tuple (player2_name, marble-color))
                player1_name (str)
                marble-color (str "W", "B", or "R")

        The KubaGame class handles all the game logic, stores the board, turn, and the winner of the game. The class
        communicates primarily within itself but sometimes reaches to the Marble class to get information about a
        particular marble.

        Game Rules:
            - Number of players:
                * Two
            - Any player can start the game
            - General Play:
                * Players take alternating turns pushing marbles in any orthogonal direction (Forward, Backward, Right, Left)
                    - To push a marble:
                        * You need an empty space (or the edge of the board) on the side you are pushing away from
                        * A player may not undo a move the opponent just made
            - Game ends when a player wins:
                * A players wins by pushing off thus capturing seven neutral red marbles
                * or by pushing off all of the opposing stones
                * A player who has no legal moves available has lost the game
        """

    def __init__(self, p1, p2):
        """
        Initializes private data members in the KubaGame class.

        self._player_info (dictionary):
            stores both player names and their corresponding color with names as keys and colors as values

        self._captured (dictionary):
            stores the number of captured red marbles each player has with names as keys and counting integers as values

        self._current_turn (str):
            initialized to None the current turn variable stores the name of the player whose turn it currently is

        self._previous_move (Dictionary)
            Stores the previous board after the corresponding players turn. Player names are keys and
            dictionaries are values

        self._won (str)
            Initialized to None the win variables stores the name of the player who won the game

        self._board (dictionary):
            stores all the marbles on the board. Coordinates as tuples are keys and marble objects are values,
            if the position is empty the value is None. This variable is hard coded to save computing time and since the
            board is the same for every game.
        """
        print(Color.CRED + "Initalizing,", KubaGame.__name__ + Color.CEND)

        self._player_info = {p1[0]: p1[1], p2[0]: p2[1]}
        self._captured = {p1[0]: 0, p2[0]: 0}

        self._current_turn = None

        self._previous_move = {p1[0]: None, p2[0]: None}

        self._won = None
        self._board = {
            (0, 0): Marble(0, 0, 'W'), (0, 1): Marble(0, 1, 'W'), (0, 2): None, (0, 3): None, (0, 4): None,
            (0, 5): Marble(0, 5, 'B'), (0, 6): Marble(0, 6, 'B'),

            (1, 0): Marble(1, 0, 'W'), (1, 1): Marble(1, 1, 'W'), (1, 2): None, (1, 3): Marble(1, 3, 'R'),
            (1, 4): None, (1, 5): Marble(1, 5, 'B'), (1, 6): Marble(1, 6, 'B'),

            (2, 0): None, (2, 1): None, (2, 2): Marble(2, 2, 'R'), (2, 3): Marble(2, 3, 'R'), (2, 4): Marble(2, 4, 'R'),
            (2, 5): None, (2, 6): None,

            (3, 0): None, (3, 1): Marble(3, 1, 'R'), (3, 2): Marble(3, 2, 'R'), (3, 3): Marble(3, 3, 'R'),
            (3, 4): Marble(3, 4, 'R'), (3, 5): Marble(3, 5, 'R'), (3, 6): None,

            (4, 0): None, (4, 1): None, (4, 2): Marble(4, 2, 'R'), (4, 3): Marble(4, 3, 'R'), (4, 4): Marble(4, 4, 'R'),
            (4, 5): None, (4, 6): None,

            (5, 0): Marble(5, 0, 'B'), (5, 1): Marble(5, 1, 'B'), (5, 2): None, (5, 3): Marble(5, 3, 'R'), (5, 4): None,
            (5, 5): Marble(5, 5, 'W'), (5, 6): Marble(5, 6, 'W'),

            (6, 0): Marble(6, 0, 'B'), (6, 1): Marble(6, 1, 'B'), (6, 2): None, (6, 3): None, (6, 4): None,
            (6, 5): Marble(6, 5, 'W'), (6, 6): Marble(6, 6, 'W')
        }

        ### Pygame
        self.selected = None
        self.valid_moves = None
        self.move_positions = []

    def make_move(self, player_name, coordinate, direction):
        """
        This method attempts to make a move on the board, it handles logic as well as communicating and getting
        information form helper methods.

        Parameters:
            player_name (str)
            coordinate (tuple (row, col))
            direction (str ('L', 'R', 'F', 'B'"))

        1. First these parameters are passed to the helper method validate_make_move_parameters. Where the parameters
        are validated and things like the current turn are checked.

        2. After Validating the move The move is passed the helper method push. That pushed the marble at the parameter
        coordinate in the direction specified.

        3. Then by comparing the opposing players previous move we validate that this move didn't violate the KO Rule.
            - "A player may not undo a move the opponent just made."

        5. if the move is successful we update the board and the positions of all the marbles on the board.

        6. Swap the current turn

        7. Check to see if anyone has won the game.

        return:
            true (if move was successfully made)
            false (otherwise)
        """
        print(Color.CRED + "Method Called:", KubaGame.make_move.__name__ + Color.CEND)
        # Valid Move check function
        if not self.validate_make_move_parameters(player_name, coordinate, direction):
            print(Color.CRED + "-----------------Validation Failed-------------------" + Color.CEND)
            return False
        # push function
        print("     Validation Passed\n")
        move = self.push_marble(player_name, coordinate, direction)
        if move is False:
            return False

        # KO RULE
        if self._previous_move[player_name] == move:
            print(Color.CRED + "-----------------KO RULE VIOLATED-------------------" + Color.CEND)
            return False
        print("     KO Passed")

        # update
        self._previous_move[player_name] = move.copy()

        self._board = move

        for pos in self._board:
            obj = self.get_marble_object(pos)
            if obj is not None:
                obj.move(pos)

        print(Color.CVIOLET + "***Move Was Successful***" + Color.CEND)
        self.display()
        for name in self._player_info:
            if name != player_name:
                self._current_turn = name


        possible_moves = []
        for position in self._board:
            if self._board[position] is not None:
                if self._board[position].get_color() == self._player_info[self._current_turn]:
                    if self.get_valid_moves(self._board[position]) is not None:
                        # add the moves to the total possible moves
                        possible_moves.append(self.get_valid_moves(self._board[position]))
                        # if a move is found break form the for loop since we know there are still viable moves
                        break

        print(possible_moves)
        if not possible_moves:
            self._won = player_name

        if self._captured[player_name] == 7:
            self._won = player_name
            print(Color.CVIOLET + "WINNER:", self._won + Color.CEND)

        if self._player_info[player_name] == "W":
            # check count of back marbles
            marble_count_index = 1
        else:
            # check count of white marbles
            marble_count_index = 0

        if self.get_marble_count()[marble_count_index] == 0:
            self._won = player_name
            print(Color.CVIOLET + "WINNER:", self._won + Color.CEND)

    def validate_make_move_parameters(self, player_name, coordinate, direction):
        """
        Parameters:
            player_name (str)
            coordinate (tuple (row, col))
            direction (str ('L', 'R', 'F', 'B'"))

        Valid Move Checks:
            - Ensures no one has won the game yet
            - ensures the player name is valid and is one of the two provided in the initialization of the game
            - Checks to see if its the player making the moves turn
            - checks to see if the parameter direction is correct
            - checks to see if the coordinate is on the board
            - checks to see if the coordinate is for an empty space
            - Ensured that an empty space (or the edge of the board) is on the side being pushed away from
        ** if any tests fail the method returns False **

        Returns:
            True if all the validations pass
            False if one doesn't
        """

        print(Color.CBOLD + "    Method Called:", KubaGame.validate_make_move_parameters.__name__ + Color.CEND)

        move = coordinate, player_name, direction
        print("     MOVE IS:", move)

        # Makes sure there isn't currently a winner
        if self.get_winner() is not None:
            return False

        # Make sure the player name is one of the two players
        if player_name not in self._player_info:
            print("Player name not found, ", move, "\n      ", player_name, "is not a player in this game")
            return False

        # Checks to see if its the turn of the current player
        if self._current_turn is None:
            self._current_turn = player_name

        if player_name != self._current_turn:
            print("Not your turn, ", move, "It is currently, ", self._current_turn, "'s turn")
            return False

        # Checks to see if the direction inputted is valid
        valid_directions = ('L', 'R', 'F', 'B')
        if direction.upper() not in valid_directions:
            print("Direction is not valid, valid directions are:\n   'L', 'R', 'F', 'B'")
            return False

        # Checks to see if the coordinate is in the board
        if coordinate not in self._board:
            print("Coordinate is not on the board", move)
            return False

        marble = self._board[coordinate]
        # checks to see if the position is not empty
        if marble is None:
            print("Position at", coordinate, "is empty")
            return False

        # Checks to see if the position in the opposite direction of the parameter position is either an edge or empty
        marble_opposite_direction = self.get_marble_object(
            self.get_coordinate_in_direction(marble, self.get_opposite_direction(direction)))
        if marble_opposite_direction is not False and marble_opposite_direction is not None:
            print("cant push this marble, ", marble, "because ",
                  self.get_coordinate_in_direction(marble, self.get_opposite_direction(direction)), marble_opposite_direction)
            return False

        # checks to see if the color of the marble being moved is the color of the player making the move
        if marble.get_color() != self._player_info[player_name]:
            print("Cant push this marble its the wrong color, ", player_name, "'s color is",
                  self._player_info[player_name])
            return False

        return True

    def push_marble(self, player_name, coordinate, direction):
        """
        Parameters:
            player_name (str)
            coordinate (tuple (row, col))
            direction (str ('L', 'R', 'F', 'B'"))

        Return:
            A copy of the board with the parameter move made
            False if the move results in pushing a marble the same color as the player marble off the board

        """
        print(Color.CBOLD + "    Method Called:", KubaGame.push_marble.__name__ + Color.CEND)

        marble = self._board[coordinate]
        print("     Push", marble, direction)

        # make a copy of the board to make the move on
        move_copy = self._board.copy()

        move_copy[coordinate] = None
        next_coord = self.get_coordinate_in_direction(marble, direction)
        print(next_coord, self.get_marble_object(next_coord))
        if self.get_marble_object(next_coord) is None:
            move_copy[next_coord] = self._board[coordinate]
        else:
            while self.get_marble_object(next_coord):
                print("         Position:", next_coord, "=", self._board[coordinate])
                move_copy[next_coord] = self._board[coordinate]
                coordinate = next_coord
                next_coord = self.get_coordinate_in_direction(self._board[next_coord], direction)

                if self.get_marble_object(next_coord) is None:
                    print("        ", next_coord, "(Next Marble) is None")
                    print("             Position:", next_coord, "=", self._board[coordinate])
                    move_copy[next_coord] = self._board[coordinate]
                elif self.get_marble_object(next_coord) is False:
                    print("        ", next_coord, "(Next Marble) is on Edge")
                    if self._player_info[player_name] == self._board[coordinate].get_color():
                        print(Color.CRED + "-----------------CANT PUSH YOUR OWN MARBLE OFF THE BOARD-------------------" + Color.CEND)
                        return False
                    elif self._board[coordinate].get_color() == "R":
                        print(Color.CVIOLET + "     ", player_name, " scored" + Color.CEND)
                        self._captured[player_name] += 1

        return move_copy

    def get_coordinate_in_direction(self, marble, direction):
        """
        This method is a helper method for the make_move method.
        Gets the coordinate in a certain direction. This method communicates with the marble class to get
        information about the parameter marble

        Parameters:
            marble (marble object form Marble class)
            direction (str ('L', 'R', 'F', 'B'"))

        Return:
            - if there is a position in the board in that direction then we return a tuple (row, col).
            - else return the tuple (-1, -1) meaning that anything in the parameter direction is pointing to the edge of
             the boarder.
        """
        if direction == "R":
            row = marble.get_row()
            col = marble.get_col() + 1
            if (row, col) in self._board:
                return row, col
            else:
                return -1, -1
        if direction == "L":
            row = marble.get_row()
            col = marble.get_col() - 1
            if (row, col) in self._board:
                return row, col
            else:
                return -1, -1
        if direction == "F":
            row = marble.get_row() - 1
            col = marble.get_col()
            if (row, col) in self._board:
                return row, col
            else:
                return -1, -1
        if direction == "B":
            row = marble.get_row() + 1
            col = marble.get_col()
            if (row, col) in self._board:
                return row, col
            else:
                return -1, -1

    def get_opposite_direction(self, direction):
        """
        This method takes a direction as a parameter and return the opposite direction.

        Parameter:
            direction (str ('L', 'R', 'F', 'B'"))

        Return:
            direction (str ('L', 'R', 'F', 'B'"))
        """
        if direction == "R":
            return "L"
        if direction == "L":
            return "R"

        if direction == "F":
            return "B"
        if direction == "B":
            return "F"

    def get_marble_object(self, coordinate):
        """
        This method takes a coordinate as a parameter and returns either the object marble at the given coordinate
        or False if the Coordinate is invalid.

        Parameter:
            coordinate (tuple (row, col))

        Return:
            marble obj
            or
            False
        """
        if coordinate in self._board:
            return self._board[coordinate]
        else:
            return False

    def get_marble(self, coordinate):
        """
        This method takes a coordinate as a parameter and returns the color of the marble at the coordinate if there is
        no marble at the given coordinate it will return 'X'

        Parameter:
            coordinate (tuple (row, col))

        Return:
            str
        """
        if coordinate in self._board:
            if self._board[coordinate] is None:
                return 'X'
            else:
                return self._board[coordinate].get_color()

    def get_marble_count(self):
        """
        This method counts the number of marbles on the board and returns a tuple of the (white marble count,
        black marble count, red marble count)
        """
        r_count = 0
        w_count = 0
        b_count = 0
        for position in self._board:
            if self._board[position] is not None:
                if self._board[position].get_color() == "R":
                    r_count += 1
                if self._board[position].get_color() == "W":
                    w_count += 1
                if self._board[position].get_color() == "B":
                    b_count += 1
        return w_count, b_count, r_count

    def get_current_turn(self):
        """
        This method returns the current turn and takes no parameters.
        """
        return self._current_turn

    def get_winner(self):
        """
        This method returns the value stored in the self._won variable which if a player has won will return that
        players name.
        """
        return self._won

    def get_captured(self, player_name):
        """
        This method takes a player name as a parameter and returns a counting integer of the number of red marbles that
        player has captured.

        Parameter:
            player_name (str)

        Return:
            number of captured marbles (int)
        """
        return self._captured[player_name]

    def display(self):
        """
        The display method prints out the board and is used for debugging.
        """
        count = 0
        row = []
        for n in self._board:
            row.append(self._board[n])
            count += 1
            print_str = ""
            if count % 7 == 0:
                for element in row:
                    if element is not None:
                        element = element.get_color()
                    else:
                        blank = Color.CGREY + "O " + Color.CEND
                        print_str += blank

                    if element == "R":
                        red = Color.CRED + "R " + Color.CEND
                        print_str += red
                    if element == "W":
                        white = Color.CBOLD + "W " + Color.CEND
                        print_str += white
                    if element == "B":
                        black = Color.CVIOLET + "B " + Color.CEND
                        print_str += black
                print(print_str)
                row = []
        print()

    def get_all_marbles(self):
        """
        Returns a list of all non-None marbles on the board.
        
        Return:
            list of Marble objects
        """
        return [marble for marble in self._board.values() if marble is not None]


    ### PYGAME

    def update(self, win):
        font = pygame.font.SysFont('Arial', 15)
        font2 = pygame.font.SysFont('Arial', 100)
        score = font.render("White:" + str(self.get_captured("PA")), True, (0, 0, 0))
        score2 = font.render("Black:" + str(self.get_captured("PB")), True, (0, 0, 0))
        winner = font2.render("Winner:" + str(self.get_winner()), True, (41, 204, 63))

        self.draw_board(win)

        self.draw_marbles(win)

        self.draw_valid_moves(self.valid_moves, win)
        # update board
        win.blit(score2, (15, 35))
        win.blit(score, (15, 15))
        if self.get_winner() is not None:
            win.blit(winner, (200, 200))
        pygame.display.update()

    def draw_board(self, win):
        # Create Background
        win.fill(GREY_1)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, GREY_2, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_marbles(self, win):
        # draw marbles
        for pos in self._board:
            marble = self._board[pos]
            if marble is not None:
                marble.draw(win)

    def get_valid_moves(self, marble):
        moves = []
        directions = ["R", "L", "F", "B"]
        for direction in directions:
            marble_in_op_direction = self.get_coordinate_in_direction(marble, self.get_opposite_direction(direction))
            if marble_in_op_direction == (-1, -1):
                if self.get_coordinate_in_direction(marble, direction) != (-1, -1):
                    moves.append(direction)
            elif self._board[marble_in_op_direction] is None:
                if self.get_coordinate_in_direction(marble, direction) != (-1, -1):
                    moves.append(direction)
        return moves

    def draw_valid_moves(self, moves, win):
        if moves is not None:
            for move in moves:
                row, col = self.get_coordinate_in_direction(self.selected, move)
                pygame.draw.circle(win, GREEN, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def select(self, name, row, col):
        print(Color.CRED + "Method Called:", KubaGame.select.__name__, "--------------------" + Color.CEND)

        print("     Selected:", Color.CBOLD + str(self.selected) + Color.CEND)
        direction = None

        if self.selected is None:

            marble = self.get_marble_object((row, col))
            print("         Selected is None\n          Clicked:", marble)
            if marble is not None and marble.get_color() == self._player_info[name]:
                print("     Select clicked marble")
                self.selected = marble
                self.selected.selected = True
                self.valid_moves = self.get_valid_moves(marble)

                print("         Find valid moves")
                for move in self.valid_moves:

                    move_direction = [self.get_coordinate_in_direction(self.selected, move), move]
                    print("             Move:", move_direction)
                    self.move_positions.append(move_direction)

            elif marble is None:
                print(Color.CRED + "-----------------Clicked Empty RESET-------------------" + Color.CEND)
                self.reset()

        elif self.selected is not None:
            print("         There is a marble selected")
            print("             Moves for selected marble are")
            for moves in self.move_positions:
                print("                 Move:", moves)
                if (row, col) == moves[0]:

                    direction = moves[1]
                    print(Color.CVIOLET + "     Clicked direction:", direction + Color.CEND)
                    break

            if direction is not None:
                print("Move", self.selected, direction)
                self.selected.selected = False
                move = self.make_move(name, (self.selected.get_row(), self.selected.get_col()), moves[1])
                self.reset()
                return True
            elif direction is None:
                print("No direction selected")
                self.reset()

        return False

    def reset(self):
        if self.selected is not None:
            self.selected.selected = False
        self.selected = None
        self.valid_moves = None
        self.move_positions = []

    def get_prev_move(self):
        return self._previous_move