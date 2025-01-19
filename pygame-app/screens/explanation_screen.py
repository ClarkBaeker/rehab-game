import pygame
from screens.screen_interface import ScreenInterface
from utils.utils import render_text
from utils.invisible_button import InvisibleButton


class ExplanationScreen(ScreenInterface):
    def __init__(self, manager):
        self.manager = manager

        # Load the background with arrows
        self.background = pygame.image.load("images/explanation.png").convert()

        # Generate invisible buttons
        self.forward_button = InvisibleButton(
            manager, default_button_type="forward", callback=self.go_forward
        )
        self.back_button = InvisibleButton(
            manager, default_button_type="back", callback=self.go_back
        )

    def on_enter(self):
        super().on_enter()

    def go_back(self):
        self.manager.switch_screen("HOME_SCREEN")

    def go_forward(self):
        self.manager.switch_screen("GAME_SCREEN")

    def handle_event(self, event):  # , time_delta):
        # Delegate events to the invisible buttons
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)

    def update(self):
        super().update()

    def draw(self, surface):
        super().draw(surface)
        # Draw the background
        surface.blit(self.background, (0, 0))

        # Debug: Draw debug rectangles to verify button placement
        if self.manager.debug:
            self.back_button.draw_debug(surface)
            self.forward_button.draw_debug(surface)

    def on_exit(self):
        super().on_exit()
