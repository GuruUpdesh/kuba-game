import pygame
import os

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        font_path = os.path.join('assets', 'fonts', 'PressStart2P-Regular.ttf')
        self.font = pygame.font.Font(font_path, 24)
        self.small_font = pygame.font.Font(font_path, 16)
        self.large_font = pygame.font.Font(font_path, 48)

    def draw(self):
        self.screen.fill((200, 200, 200))
        title = self.font.render("Kuba Game", True, (0, 0, 0))
        start_text = self.font.render("Press SPACE to start", True, (0, 0, 0))
        self.screen.blit(title, (300, 200))
        self.screen.blit(start_text, (250, 300))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
        return None