import pygame
import asyncio
from game.kuba_game import KubaGame
from game.constants import WIDTH, HEIGHT
from ui.start_screen import StartScreen
from ui.game_ui import GameUI

async def main_loop():
    pygame.init()
    pygame.font.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kuba")

    start_screen = StartScreen(WIN)
    game_started = False

    while not game_started:
        start_screen.draw()
        pygame.display.flip()
        game_started = start_screen.handle_events()
        await asyncio.sleep(0)

    clock = pygame.time.Clock()
    FPS = 60
    name_1 = 'PA'
    name_2 = 'PB'
    game = KubaGame((name_1, 'W'), (name_2, 'B'))
    game_ui = GameUI(WIN, game)
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
                board_pos = game_ui.get_board_position(pos)
                if board_pos:
                    row, col = board_pos
                    if game.get_prev_move()[name_1] is None:
                        game.select(name_1, row, col)
                    else:
                        game.select(game.get_current_turn(), row, col)

        game_ui.draw()
        await asyncio.sleep(0)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main_loop())