import pygame
from utils.utils import load_image
from screens.screen_interface import ScreenInterface

class HomeScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        self.background = pygame.image.load(
            "images/start.png"
        ).convert()
                
        # Invisible button area in the middle
        button_width = 800
        button_height = 1000
        self.start_button_rect = pygame.Rect(
            (
                manager.screen_width // 2 - button_width // 2,
                manager.screen_height // 2 - button_height // 2,
            ),
            (button_width, button_height),
        )
        
        # Invisible button area in the upper left corner for the configuration file 
        button_width = 100
        button_height = 100
        self.config_button_rect = pygame.Rect(
            (
                400 - button_width // 2,
                200 - button_height // 2,
            ),
            (button_width, button_height),
        )

    def on_enter(self):
        super().on_enter()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                if self.start_button_rect.collidepoint(event.pos):
                    self.manager.switch_screen("EXPLANATION_SCREEN")
                if self.config_button_rect.collidepoint(event.pos):
                    self.manager.switch_screen("CONFIGURATION_SCREEN")

    def update(self):
        super().update()

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.background, (0, 0))
        # Debug size of invisible button
        if self.manager.debug:
            pygame.draw.rect(surface, (255, 0, 0), self.start_button_rect, 2)
            pygame.draw.rect(surface, (255, 0, 0), self.config_button_rect, 2)

    def on_exit(self):
        super().on_exit()
