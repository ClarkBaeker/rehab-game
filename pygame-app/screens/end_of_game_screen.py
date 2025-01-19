import pygame
import time
from screens.screen_interface import ScreenInterface
from utils.utils import render_text, render_centered_test, load_sound
from utils.invisible_button import InvisibleButton
from utils.logger import log_data


class EndOfGameScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        # Load the background with arrows
        self.background_5_min = pygame.image.load(
            "images/well_done_5_min.png"
        ).convert()
        self.background_20_lights = pygame.image.load(
            "images/well_done_20_lights.png"
        ).convert()

        self.feedback_buttons = {
            "happy": pygame.Rect(
                manager.screen_width // 2 - 150, manager.screen_height // 2, 50, 50
            ),
            "mid": pygame.Rect(
                manager.screen_width // 2 - 25, manager.screen_height // 2, 50, 50
            ),
            "sad": pygame.Rect(
                manager.screen_width // 2 + 100, manager.screen_height // 2, 50, 50
            ),
        }

        # Generate invisible button
        self.forward_button = InvisibleButton(
            manager, default_button_type="forward", callback=self.go_forward
        )

    def on_enter(self):
        super().on_enter()

    def go_forward(self):
        self.manager.switch_screen("FEEDBACK_SCREEN")

    def handle_event(self, event):
        self.forward_button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if user clicked a feedback button
            for fb, rect in self.feedback_buttons.items():
                if rect.collidepoint(event.pos):
                    self.manager.shared_data["feedback"] = fb
                    # Audio feedback, if button is pressed
                    if self.click_sound:
                        self.click_sound.play()

    def update(self):
        super().update()

    def draw(self, surface):
        super().draw(surface)
        surface.fill((180, 180, 180))

        # Decide what text to show
        reason = self.manager.shared_data["end_reason"]
        dots_pressed = self.manager.shared_data["dots_pressed"]

        minutes = self.manager.shared_data["duration"] // 60
        seconds = self.manager.shared_data["duration"] % 60

        if reason == "20_reached":
            # text = f"Well done! You touched all 20 dots in {minutes} minutes and {seconds} seconds."
            surface.blit(self.background_20_lights, (0, 0))
            text = f"{minutes} Minuten and {seconds} Sekunden"

        else:
            # text = f"Well done! You touched {dots_pressed} dots."
            surface.blit(self.background_5_min, (0, 0))
            text = f"{dots_pressed}"

        render_centered_test(
            surface,
            text,
            self.manager.big_letter_size,
            (255, 255, 255),
            (self.manager.screen_width // 2, self.manager.screen_height // 2 + 75),
        )

        # render_text(surface, "How did you feel during the exercise?", self.manager.minimum_letter_size, (0, 0, 0),
        #             (50, 150))

        # # Draw feedback buttons (simple squares/circles)
        # pygame.draw.circle(surface, (0, 255, 0), (self.feedback_buttons["happy"].center), 50)   # happy
        # pygame.draw.circle(surface, (255, 255, 0), (self.feedback_buttons["mid"].center), 50)   # mid
        # pygame.draw.circle(surface, (255, 0, 0), (self.feedback_buttons["sad"].center), 50)     # sad

        # # Confirm button
        # pygame.draw.rect(surface, (0, 200, 0), self.confirm_button_rect)
        # render_text(surface, "Confirm", self.manager.minimum_letter_size, (255, 255, 255),
        #             (self.confirm_button_rect.centerx - 30, self.confirm_button_rect.centery - 10))

        # Debug: Draw debug rectangles to verify button placement
        if self.manager.debug:
            self.forward_button.draw_debug(surface)

    def on_exit(self):
        super().on_exit()
