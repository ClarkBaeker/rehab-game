import pygame
from screens.screen_interface import ScreenInterface
from utils.invisible_button import InvisibleButton


class RepeatScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)
        # Just one big 'repeat' arrow in the middle
        self.repeat_rect = pygame.Rect(
            (manager.screen_width // 2 - 50, manager.screen_height // 2 - 50),
            (100, 100),
        )

        # Big repeat button in the middle
        button_width = 800
        button_height = 1000
        button_rect = pygame.Rect(
            (
                manager.screen_width // 2 - button_width // 2,
                manager.screen_height // 2 - button_height // 2,
            ),
            (button_width, button_height),
        )
        self.repeat_button = InvisibleButton(
            manager, rect=button_rect, callback=self.go_forward
        )

        # Load the background
        self.background = pygame.image.load("images/repeat.png").convert()

    def on_enter(self):
        super().on_enter()

    def handle_event(self, event):
        self.repeat_button.handle_event(event)

    def go_forward(self):
        # Reset data for new run if desired
        self.manager.switch_screen("HOME_SCREEN")

    def update(self):
        super().update()

    def draw(self, surface):
        super().draw(surface)
        # Draw the background
        surface.blit(self.background, (0, 0))

        # Debug: Draw debug rectangles to verify button placement
        if self.manager.debug:
            self.repeat_button.draw_debug(surface)

    def on_exit(self):
        super().on_exit()
