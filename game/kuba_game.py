from enum import Enum
import copy
from typing import List, Tuple, Optional

class MarbleColor(Enum):
    WHITE = 'W'
    BLACK = 'B'
    RED = 'R'

class PrintColor(Enum):
    GREY = '\33[90m'
    RED = '\33[31m'
    END = '\33[0m'
    BOLD = '\33[1m'
    VIOLET = '\33[35m'

class Direction(Enum):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, -1)
    DOWN = (0, 1)

    def opposite(self):
        opposites = {
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP
        }
        return opposites[self]

class Marble:
    def __init__(self, color: MarbleColor):
        self.color = color

    def __repr__(self):
        color = PrintColor.END
        match self.color:
            case MarbleColor.WHITE:
                color = PrintColor.END
            case MarbleColor.BLACK:
                color = PrintColor.VIOLET
            case MarbleColor.RED:
                color = PrintColor.RED

        return color.value + self.color.value + PrintColor.END.value

class Board:
    def __init__(self, game):
        self.game = game
        self.grid: List[List[Optional[Marble]]] = [[None for _ in range(7)] for _ in range(7)]
        self._initialize_board()

    def __repr__(self):
        board=""
        for row in range(7):
            for col in range(7):
                cell = self.grid[row][col]
                if cell is not None:                        
                        board += f"{cell} "
                else:
                    board += (PrintColor.GREY.value + "O " + PrintColor.END.value)
            board+="\n"
        return board

    def _initialize_board(self):
        initial_config = [
            ['W', 'W', '.', '.', '.', 'B', 'B'],
            ['W', 'W', '.', 'R', '.', 'B', 'B'],
            ['.', '.', 'R', 'R', 'R', '.', '.'],
            ['.', 'R', 'R', 'R', 'R', 'R', '.'],
            ['.', '.', 'R', 'R', 'R', '.', '.'],
            ['B', 'B', '.', 'R', '.', 'W', 'W'],
            ['B', 'B', '.', '.', '.', 'W', 'W']
        ]

        for row in range(7):
            for col in range(7):
                color = initial_config[row][col]
                if color != '.':
                    self.grid[row][col] = Marble(MarbleColor(color))

    def get_marble(self, coordinates: Tuple[int, int]) -> Optional[Marble]:
        row, col = coordinates
        return self.grid[row][col]

    def set_marble(self, coordinates: Tuple[int, int], marble: Optional[Marble]):
        row, col = coordinates
        self.grid[row][col] = marble

    def get_move(self, coordinates: Tuple[int, int], direction: Direction, check=False):
        cell = self.get_marble(coordinates)
        if cell is None:
            if not check:
                self.game._alert("Can't move an empy cell!")
            return []

        # check if marble can be pushed in this direction
        row, col = coordinates
        opposite_direction = direction.opposite()
        dx, dy = opposite_direction.value
        opposite_row, opposite_col = row + dy, col + dx

        # check if the opposite direction is empty or out of bounds
        if 0 <= opposite_row < 7 and 0 <= opposite_col < 7:
            if self.get_marble((opposite_row, opposite_col)) is not None:
                if not check:
                    self.game._alert("Can't push")
                return []

        dx, dy = direction.value
        continuous_marbles = []

        while 0 <= row < 7 and 0 <= col < 7:
            marble = self.get_marble((row, col))
            if marble is None:
                break
            continuous_marbles.append((row, col))
            row += dy
            col += dx
        
        return continuous_marbles

    def push_marbles(self, marbles: List[Tuple[int, int]], direction: Direction):
        pushed_off_marbles = []
        dx, dy = direction.value
        for i in range(len(marbles) - 1, -1 , -1):
            old_pos = marbles[i]
            new_pos = (old_pos[0] + dy, old_pos[1] + dx)
            if 0 <= new_pos[0] < 7 and 0 <= new_pos[1] < 7:
                self.set_marble(new_pos, self.get_marble(old_pos))
            else:
                pushed_off_marbles.append(self.get_marble(old_pos))
            self.set_marble(old_pos, None)

        return pushed_off_marbles

    def get_all_marbles(self, color: Optional[MarbleColor] = None) -> List[Tuple[int, int]]:
        if color is None:
            return [(row, col) for row, row_marbles in enumerate(self.grid)
                    for col, marble in enumerate(row_marbles) if marble is not None]
        else:
            return [(row, col) for row, row_marbles in enumerate(self.grid)
                    for col, marble in enumerate(row_marbles) 
                    if marble is not None and marble.color == color]

class Player:
    def __init__(self, name: str, color: MarbleColor):
        self.name = name
        self.color = color
        self.captured_red = 0
        self.previous_move: Optional[Tuple[Tuple[int, int], Direction, List[Tuple[int, int]]]] = None

    def __repr__(self):
        return f"{self.name} ({self.color.value})"

    def capture_red(self):
        self.captured_red += 1

class Alert:
    def __init__(self, message: str):
        self.message = message
    
    def __repr__(self):
        return PrintColor.RED.value + self.message + PrintColor.END.value

class KubaGame:
    def __init__(self, debug=False):
        self.players = [
            Player("You", MarbleColor("W")),
            Player("Bot", MarbleColor("B"))
        ]
        self.board = Board(self)
        self.current_player_index = 0
        self.winner = None
        self.alert = None
        self.moves = 0

        self.selected = None

        self.debug=debug

    def __repr__(self):
        game = ""
        for player in self.players:
            indicator = "←" if player == self.current_player else ""
            game += f"{player}: {player.captured_red} {indicator}\n"
        return game

    def _alert(self, message: str):
        self.alert = Alert(message)
        if self.debug:
            print(f"{self.alert}")

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def opponent(self) -> Player:
        return self.players[(self.current_player_index + 1) % 2]

    def select(self, coordinates: Tuple[int, int]):
        if self.selected:
             valid_moves = self.get_valid_moves(self.selected)
             for move in valid_moves:
                dx, dy = move[1].value
                row, col = self.selected
                row, col = row + dy, col + dx
                if (row, col) == coordinates:
                    self.make_move(self.selected, move[1])
                    self.selected = None
                    return
                         
        marble = self.board.get_marble(coordinates)
        if marble and marble.color == self.current_player.color:
            self.selected = coordinates
        else:
            self.selected = None

    def make_move(self, coordinates: Tuple[int, int], direction: Direction, check=False) -> bool:
        if self.winner:
            if not check:
                self._alert("Can't move after game is over!")
            return False

        affected_positions = self.board.get_move(coordinates, direction, check)
        if not affected_positions:
            return False

        # convert positions into marbles
        affected_marbles = [self.board.get_marble(c) for c in affected_positions]

        # check if player is moving their own marble
        if affected_marbles[0].color != self.current_player.color:
            if not check:
                self._alert(f"{self.current_player} can't move {affected_marbles[0]}!")
            return False

        # check if player is pushing off their own marble
        last_marble = affected_marbles[-1]
        last_row, last_col = affected_positions[-1]
        new_pos = (last_row + direction.value[1], last_col + direction.value[0])
        if new_pos[0] < 0 or new_pos[0] >= 7 or new_pos[1] < 0 or new_pos[1] >= 7:
            if last_marble.color == self.current_player.color:
                if not check:
                    self._alert(f"{self.current_player} can't push off their own marble!")
                return False

        # check the KO rule (can't undo opponents last move)
        if self._violates_ko_rule(coordinates, direction, affected_positions):
            if not check:
                self._alert("This move violates the KO rule!")
            return False

        # stops after validation
        if check:
            return True

        self.moves += 1

        # perform move
        pushed_off_marbles = self.board.push_marbles(affected_positions, direction)

        # update captures
        for marble in pushed_off_marbles:
            if marble.color == MarbleColor.RED:
                self.current_player.capture_red()


        self.current_player.previous_move = (coordinates, direction, affected_positions)

        # check for win conditions
        if self.current_player.captured_red >= 7:
            self.winner = self.current_player
            self._alert(f"{self.winner} wins by capturing 7 red marbles!")
        elif not self.board.get_all_marbles(self.opponent.color):
            self.winner = self.current_player
            self._alert(f"{self.winner} wins by eliminating all opponent's marbles!")

        # switch turns
        if not self.winner:
            self.current_player_index = (self.current_player_index + 1) % 2

        # if after switching there are no moves declare a winner
        if not self.winner and not self.get_valid_moves():
            self.winner = self.opponent
            self._alert(f"{self.winner} wins since opponent has no moves")

        return True

    def _violates_ko_rule(self, coordinate: Tuple[int, int], direction: Direction, affected_positions: List[Tuple[int, int]]):
        if not self.opponent.previous_move:
            return False

        prev_coord, prev_direction, prev_affected = self.opponent.previous_move

        # check if the moves interact with the same group of marbles
        if not set(affected_positions).intersection(set(prev_affected)):
            return False

        # check if the current move undoes the previous move
        if direction == prev_direction.opposite():
            # if the marbles are in the same row or column and moving in opposite directions
            if (coordinate[0] == prev_coord[0] or coordinate[1] == prev_coord[1]):
                return True

        return False

    def get_valid_moves(self, cord=None):
        cords = [cord]
        if not cord:
            cords = self.board.get_all_marbles(self.current_player.color)
        moves = []
        for c in cords:
            for direction in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
                if self.make_move(c, direction, True):
                    moves.append((c, direction))
        return moves

    def get_game_state(self):
        white = len(self.board.get_all_marbles(MarbleColor.WHITE))
        black = len(self.board.get_all_marbles(MarbleColor.BLACK))
        red = len(self.board.get_all_marbles(MarbleColor.RED))
        return {
            MarbleColor.WHITE.value: white,
            MarbleColor.BLACK.value: black,
            MarbleColor.RED.value: red
        }

    def clone(self):
        # Create a new instance of KubaGame
        cloned_game = KubaGame()

        # Copy the board state
        cloned_game.board = Board(cloned_game)
        for row in range(7):
            for col in range(7):
                cloned_game.board.grid[row][col] = copy.deepcopy(self.board.grid[row][col])

        # Copy players
        cloned_game.players = [
            Player(player.name, player.color) for player in self.players
        ]
        for original_player, cloned_player in zip(self.players, cloned_game.players):
            cloned_player.captured_red = original_player.captured_red
            cloned_player.previous_move = copy.deepcopy(original_player.previous_move)

        # Copy game state
        cloned_game.current_player_index = self.current_player_index
        cloned_game.winner = self.winner
        cloned_game.alert = copy.deepcopy(self.alert)
        cloned_game.moves = self.moves
        cloned_game.selected = self.selected

        return cloned_game


if __name__ == "__main__":
    game = KubaGame()
