import pygame
from kubagame import KubaGame, Marble

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 7, 7
SQUARE_SIZE = WIDTH // COLS

RED = (255, 0, 0)
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)
GREY_1 = (128, 128, 128)
GREY_2 = (169, 169, 169)
BLUE = (255, 255, 255)
GREEN = (0, 255, 0)

pygame.init()
pygame.font.init()

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kuba")


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def main():

    run = True
    clock = pygame.time.Clock()
    name_1 = 'PA'
    name_2 = 'PB'
    game = KubaGame((name_1, 'W'), (name_2, 'B'))
    count_click = 0
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                count_click += 1
                print(count_click)
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if game.get_prev_move()[name_1] is None:
                    game.select(name_1, row, col)
                else:
                    game.select(game.get_current_turn(), row, col)

        game.update(WIN)
    pygame.quit()


main()
