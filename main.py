import pygame
import asyncio
from ai.kuba_ai import train_ai
from game.kuba_game import KubaGame
from ui.start_screen import StartScreen
from ui.game_ui import GameUI

WIDTH, HEIGHT = 1600, 900

async def main_loop():
    pygame.init()
    pygame.font.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kuba")

    print("Training AI... This may take a while.")
    trained_ai = train_ai()
    print("AI training complete!")


    start_screen = StartScreen(WIN)
    game_started = False

    while not game_started:
        start_screen.draw()
        pygame.display.flip()
        game_started = start_screen.handle_events()
        await asyncio.sleep(0)

    clock = pygame.time.Clock()
    FPS = 60
    game = KubaGame()
    game_ui = GameUI(WIN, game)
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                board_pos = game_ui.get_board_position(pos)
                if board_pos:
                    game.select(board_pos)
        
        if game.current_player.name == "Bot" and not game.winner:
            action = trained_ai.get_action(game)
            coordinates, direction = action
            game.make_move(coordinates, direction)
            # await asyncio.sleep(0.5)

        game_ui.draw()
        await asyncio.sleep(0)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main_loop())
    # ai = train_ai()