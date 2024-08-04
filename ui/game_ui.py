import pygame
import os
from game.constants import WIDTH, HEIGHT, BOARD_SIZE, GREEN, BLUE, ROWS, COLS, RED, WHITE, BLACK, GREY_1, GREY_2, BACKGROUND

class GameUI:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.board_size = min(screen.get_width(), screen.get_height()) * 0.8
        self.square_size = self.board_size // ROWS
        self.board_offset = ((screen.get_width() - self.board_size) // 2, (screen.get_height() - self.board_size) // 2)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Load the pixel font
        font_path = os.path.join('assets', 'fonts', 'PressStart2P-Regular.ttf')
        self.font = pygame.font.Font(font_path, 24)
        self.small_font = pygame.font.Font(font_path, 16)
        self.large_font = pygame.font.Font(font_path, 48)

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.draw_board()
        self.draw_marbles()
        self.draw_valid_moves()
        self.draw_player_info('PA', 50)
        self.draw_player_info('PB', self.screen.get_width() - 250)
        self.draw_current_turn()
        pygame.display.flip()

    def draw_board(self):
        board_surface = pygame.Surface((self.board_size, self.board_size))
        board_surface.fill(GREY_1)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(board_surface, GREY_2, 
                                (col * self.square_size, row * self.square_size, 
                                self.square_size, self.square_size))
        self.screen.blit(board_surface, self.board_offset)

        for row in range(ROWS):
            for col in range(COLS):
                marble = self.game.get_marble((row, col))
                if marble != 'X':
                    color = RED if marble == 'R' else (WHITE if marble == 'W' else BLACK)
                    pygame.draw.circle(board_surface, color,
                                       ((col + 0.5) * self.square_size, (row + 0.5) * self.square_size),
                                       self.square_size * 0.4)

        self.screen.blit(board_surface, self.board_offset)

    def draw_marbles(self):
        for pos, marble in self.game._board.items():
            if marble is not None:
                row, col = pos
                x = self.board_offset[0] + col * self.square_size + self.square_size // 2
                y = self.board_offset[1] + row * self.square_size + self.square_size // 2
                color = RED if marble.get_color() == 'R' else (WHITE if marble.get_color() == 'W' else BLACK)
                
                if marble == self.game.selected:
                    pygame.draw.circle(self.screen, GREEN, (x, y), self.square_size // 2 - 2)
                
                pygame.draw.circle(self.screen, color, (x, y), self.square_size // 2 - 5)

    def draw_valid_moves(self):
        if self.game.valid_moves:
            for move in self.game.valid_moves:
                row, col = self.game.get_coordinate_in_direction(self.game.selected, move)
                x = self.board_offset[0] + col * self.square_size + self.square_size // 2
                y = self.board_offset[1] + row * self.square_size + self.square_size // 2
                pygame.draw.circle(self.screen, GREEN, (x, y), 15)

    def draw_player_info(self, player, x):
        color = self.game._player_info[player]
        bg_color = WHITE if color == 'W' else BLACK
        text_color = BLACK if color == 'W' else WHITE
        pygame.draw.rect(self.screen, bg_color, (x, 50, 200, 50))
        text = self.font.render(f"Player {player}", True, text_color)
        self.screen.blit(text, (x + 10, 60))

        score = self.game.get_captured(player)
        text = self.small_font.render(f"Score: {score}", True, BLACK)
        self.screen.blit(text, (x + 10, 110))

        self.draw_captured_marbles(player, x, 160)

    def draw_captured_marbles(self, player, x, y):
        red_captured = self.game.get_captured(player)
        opponent = 'PB' if player == 'PA' else 'PA'
        opponent_color = self.game._player_info[opponent]
        opponent_captured = 8 - len([m for m in self.game.get_all_marbles() if m.get_color() == opponent_color])

        text = self.small_font.render("Captured:", True, BLACK)
        self.screen.blit(text, (x + 10, y))

        for i in range(red_captured):
            pygame.draw.circle(self.screen, RED, (x + 20 + i * 25, y + 30), 10)

        for i in range(opponent_captured):
            pygame.draw.circle(self.screen, BLACK if opponent_color == 'B' else WHITE, (x + 20 + i * 25, y + 60), 10)

    def draw_current_turn(self):
        current_turn = self.game.get_current_turn()
        if current_turn:
            text = self.font.render(f"Current Turn: {current_turn}", True, BLACK)
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 10))

    def draw_winner(self):
        winner = self.game.get_winner()
        if winner:
            text = self.large_font.render(f"Winner: {winner}", True, (41, 204, 63))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 
                                    self.screen.get_height() // 2 - text.get_height() // 2))

    def get_board_position(self, mouse_pos):
        x, y = mouse_pos
        board_x = x - self.board_offset[0]
        board_y = y - self.board_offset[1]
        
        if 0 <= board_x < self.board_size and 0 <= board_y < self.board_size:
            return int(board_y // self.square_size), int(board_x // self.square_size)
        return None