import pygame
import time
from screens.screen_interface import ScreenInterface
from utils.utils import load_sound
from utils.invisible_button import InvisibleButton


class FeedbackScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        # Load the background with arrows
        self.feedback = pygame.image.load("images/feedback.png").convert()
        self.feedback_good = pygame.image.load("images/feedback_good.png").convert()
        self.feedback_bad = pygame.image.load("images/feedback_bad.png").convert()
        self.feedback_medium = pygame.image.load("images/feedback_medium.png").convert()
        self.current_screen = self.feedback

        # Define feedback rectangles and get their invisible buttons
        feedback_boxes_size = 350
        feedback_boxes_distance = 380
        y_pos = manager.screen_height // 2 - 100

        self.feedback_rect = {
            "happy": pygame.Rect(
                manager.screen_width // 2
                - feedback_boxes_size // 2
                + feedback_boxes_distance,
                y_pos,
                feedback_boxes_size,
                feedback_boxes_size,
            ),
            "medium": pygame.Rect(
                manager.screen_width // 2 - feedback_boxes_size // 2,
                y_pos,
                feedback_boxes_size,
                feedback_boxes_size,
            ),
            "sad": pygame.Rect(
                manager.screen_width // 2
                - feedback_boxes_size // 2
                - feedback_boxes_distance,
                y_pos,
                feedback_boxes_size,
                feedback_boxes_size,
            ),
        }
        self.feedback_buttons = {
            "happy": InvisibleButton(
                manager,
                rect=self.feedback_rect["happy"],
                callback=lambda: self.use_feedback("happy"),
            ),
            "medium": InvisibleButton(
                manager,
                rect=self.feedback_rect["medium"],
                callback=lambda: self.use_feedback("medium"),
            ),
            "sad": InvisibleButton(
                manager,
                rect=self.feedback_rect["sad"],
                callback=lambda: self.use_feedback("sad"),
            ),
        }

        # Generate invisible button
        self.forward_button = InvisibleButton(
            manager, default_button_type="forward", callback=self.go_forward
        )
        self.back_button = InvisibleButton(
            manager, default_button_type="back", callback=self.go_back
        )

        # Sounds
        self.click_sound = load_sound("sounds/mouse-click.mp3")

    def on_enter(self):
        super().on_enter()
        self.current_screen = self.feedback

    def go_forward(self):
        # Log data
        self.manager.logger.log_shared_data(self.manager.shared_data)

        # Remove shared data that is specific to game
        self.manager.game.rmv_shared_data()

        # Debug: Print feedback
        if self.manager.debug:
            print("Feedback: ", self.manager.shared_data["feedback"])

        # Switch to repeat screen
        self.manager.switch_screen("REPEAT_SCREEN")

    def go_back(self):
        self.manager.switch_screen("END_OF_GAME_SCREEN")

    def use_feedback(self, feedback):
        # Set feedback in shared data. Will be overwritten if user clicks another feedback button
        self.manager.shared_data["feedback"] = feedback

        # Change screen to show selection
        if feedback == "happy":
            self.current_screen = self.feedback_good
            print("currently handling", feedback)
        elif feedback == "medium":
            self.current_screen = self.feedback_medium
            print("currently handling", feedback)
        elif feedback == "sad":
            self.current_screen = self.feedback_bad
            print("currently handling", feedback)
        else:
            self.current_screen = self.feedback

        # Audio feedback, if button is pressed
        if self.click_sound:
            self.click_sound.play()

    def handle_event(self, event):

        # Delegate events to the invisible buttons
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)
        self.feedback_buttons["happy"].handle_event(event)
        self.feedback_buttons["medium"].handle_event(event)
        self.feedback_buttons["sad"].handle_event(event)

    def update(self):
        super().update()

    def draw(self, surface):
        super().draw(surface)
        # Draw the background
        surface.blit(self.current_screen, (0, 0))

        # Debug: Draw debug rectangles to verify button placement
        if self.manager.debug:
            self.forward_button.draw_debug(surface)
            self.back_button.draw_debug(surface)
            for feedback_name, button in self.feedback_buttons.items():
                button.draw_debug(surface)

    def on_exit(self):
        super().on_exit()
