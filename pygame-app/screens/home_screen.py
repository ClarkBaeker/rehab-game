import pygame
import os
from utils.utils import load_image

class HomeScreen:
    def __init__(self, manager):
        self.manager = manager
        self.background = load_image("images/start.png")
        # Invisible button area in the middle
        
        button_width = 800
        button_height = 1000
        self.button_rect = pygame.Rect(
            (manager.screen_width // 2 - button_width // 2, manager.screen_height // 2 - button_height // 2),
            (button_width, button_height)
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                if self.button_rect.collidepoint(event.pos):
                    self.manager.switch_screen("EXPLANATION_SCREEN")

    def update(self):
        pass

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        # Debug size of invisible button
        if self.manager.debug:
            pygame.draw.rect(surface, (255, 0, 0), self.button_rect, 2)
