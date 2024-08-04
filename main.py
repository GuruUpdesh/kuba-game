import pygame
import asyncio
from game.kuba_game import KubaGame
from game.constants import WIDTH, HEIGHT, SQUARE_SIZE

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


async def main_loop():
    pygame.init()
    pygame.font.init()

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kuba")

    clock = pygame.time.Clock()
    FPS = 60
    name_1 = 'PA'
    name_2 = 'PB'
    game = KubaGame((name_1, 'W'), (name_2, 'B'))
    count_click = 0
    run = True

    while run:
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
        await asyncio.sleep(0)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main_loop())
