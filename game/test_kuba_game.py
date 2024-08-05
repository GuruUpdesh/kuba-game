import unittest
from kuba_game import KubaGame, MarbleColor, Direction

class TestKubaGame(unittest.TestCase):

    def setUp(self):
        self.game = KubaGame(debug=True)

    def test_initial_board_state(self):
        state = self.game.get_game_state()
        self.assertEqual(state, {'W': 8, 'B': 8, 'R': 13})

    def test_valid_move(self):
        self.assertTrue(self.game.make_move((0, 0), Direction.RIGHT))
        state = self.game.get_game_state()
        self.assertEqual(state, {'W': 8, 'B': 8, 'R': 13})

    def test_invalid_move_empty_cell(self):
        self.assertFalse(self.game.make_move((2, 0), Direction.RIGHT))

    def test_invalid_move_out_of_bounds(self):
        self.assertFalse(self.game.make_move((-1, 0), Direction.RIGHT))

    def test_invalid_move_opponent_marble(self):
        self.assertFalse(self.game.make_move((0, 6), Direction.LEFT))

    def test_invalid_move_red_marble(self):
        self.assertFalse(self.game.make_move((1, 3), Direction.LEFT))

    def test_capture_red_marble(self):
        # Setup: Move a white marble to push a red marble off
        self.game.make_move((0, 0), Direction.RIGHT)
        self.game.make_move((0, 6), Direction.DOWN)
        self.game.make_move((0, 1), Direction.RIGHT)
        self.game.make_move((1, 6), Direction.DOWN)
        self.game.make_move((0, 3), Direction.DOWN)
        self.game.make_move((2, 6), Direction.DOWN)
        self.game.make_move((1, 3), Direction.DOWN)
        
        self.assertEqual(self.game.players[0].captured_red, 1)
        state = self.game.get_game_state()
        self.assertEqual(state, {'W': 8, 'B': 8, 'R': 12})

    def test_ko_rule(self):
        # Setup: Make a move
        self.game.make_move((0, 0), Direction.RIGHT)
        self.game.make_move((0, 6), Direction.LEFT)
        self.game.make_move((0, 1), Direction.RIGHT)
        # Try to undo opponent's last move
        self.assertFalse(self.game.make_move((0, 5), Direction.RIGHT))

    def test_win_by_capturing_red_marbles(self):
        # This test would be quite long, so let's just check if the winner is set
        self.game.players[0].captured_red = 7
        self.game.make_move((0, 0), Direction.RIGHT)
        self.assertEqual(self.game.winner, self.game.players[0])

    def test_win_by_eliminating_opponent_marbles(self):
        # This test would also be quite long, so we'll simulate it
        for i in range(7):
            for j in range(7):
                if self.game.board.grid[i][j] and self.game.board.grid[i][j].color == MarbleColor.BLACK:
                    self.game.board.grid[i][j] = None
        self.game.make_move((0, 0), Direction.RIGHT)  # Any valid move
        self.assertEqual(self.game.winner, self.game.players[0])

if __name__ == '__main__':
    unittest.main()