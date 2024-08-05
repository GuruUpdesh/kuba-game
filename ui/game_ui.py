import select
import pygame
import os
from game import marble
import game
from game.constants import BLUE, GREEN, ROWS, COLS, RED, WHITE, BLACK, GREY_1, GREY_2, BACKGROUND
from game2.kuba_game import KubaGame

class GameUI:
    def __init__(self, screen, game: KubaGame):
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
        self.draw_player_info('You', 50)
        self.draw_player_info('Bot', self.screen.get_width() - 300)
        self.draw_winner()
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

    def draw_marbles(self):
        for row in range(7):
            for col in range(7):
                marble = self.game.board.get_marble((row, col))
                if marble is not None:
                    x = self.board_offset[0] + col * self.square_size + self.square_size // 2
                    y = self.board_offset[1] + row * self.square_size + self.square_size // 2
                    radius = self.square_size // 2 - 5
            
                    if marble.color.value == "R":
                        base_color = RED
                        gradient_color = (255, 150, 150)
                    elif marble.color.value == "W":
                        base_color = WHITE
                        gradient_color = (220, 220, 220)
                    elif marble.color.value == "B":
                        base_color = BLACK
                        gradient_color = (100, 100, 100)

                    # draw selection circle
                    if self.game.selected == (row, col):
                        pygame.draw.circle(self.screen, GREEN, (int(x), int(y)), radius + 2)
                    elif marble.color == self.game.current_player.color:
                        pygame.draw.circle(self.screen, BLUE, (int(x), int(y)), radius + 2)

                    # draw gradient
                    for i in range(int(radius), 0, -1):
                        ratio = i / radius
                        color = [int(base_color[j] * ratio + gradient_color[j] * (1 - ratio)) for j in range(3)]
                        pygame.draw.circle(self.screen, color, (int(x), int(y)), i)


    def draw_valid_moves(self):
        if not self.game.selected:
            return
        
        valid_moves = self.game.get_valid_moves(self.game.selected)
        for move in valid_moves:
            dx, dy = move[1].value
            row, col = self.game.selected
            row, col = row + dy, col + dx
            x = self.board_offset[0] + col * self.square_size + self.square_size // 2
            y = self.board_offset[1] + row * self.square_size + self.square_size // 2
            pygame.draw.circle(self.screen, GREEN, (x, y), 15)

    def draw_player_info(self, player_name, x):
        player = None
        if self.game.players[0].name == player_name:
            player = self.game.players[0]
        else:
            player = self.game.players[1]

        color = player.color
        bg_color = WHITE if color.value == 'W' else BLACK
        text_color = BLACK if color.value == 'W' else WHITE
        pygame.draw.rect(self.screen, bg_color, (x, 50, 250, 50))
        text = self.font.render(f"{player}", True, text_color)
        self.screen.blit(text, (x + 10, 60))

        score = player.captured_red
        text = self.small_font.render(f"Score: {score}", True, BLACK)
        self.screen.blit(text, (x + 10, 110))

        # self.draw_captured_marbles(player, x, 160)

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

    def draw_winner(self):
        winner = self.game.winner
        if winner:
            text = self.large_font.render(f"Winner: {winner.name}", True, (41, 204, 63))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 
                                    self.screen.get_height() // 2 - text.get_height() // 2))

    def get_board_position(self, mouse_pos):
        x, y = mouse_pos
        board_x = x - self.board_offset[0]
        board_y = y - self.board_offset[1]
        
        if 0 <= board_x < self.board_size and 0 <= board_y < self.board_size:
            return int(board_y // self.square_size), int(board_x // self.square_size)
        return None