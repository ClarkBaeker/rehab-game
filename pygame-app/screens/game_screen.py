import pygame
import time
from utils.utils import render_text, load_sound
from utils.invisible_button import InvisibleButton
import random

class GameScreen:
    def __init__(self, manager):
        self.manager = manager

        # Load the background with arrows
        self.background = pygame.image.load("images/game.png").convert()
        
        # Define how often to press dots to "win" the game. Currently the screen is still hardcoded to 20 dots.
        self.how_often_to_press_dots = 20
        if self.manager.debug: 
            self.how_often_to_press_dots = 3
            
        # Define how the game maximal goes. Currently the screen is still hardcoded to 5 minutes.
        self.how_long = 5 * 60  # 5 minutes
        if self.manager.debug: 
            self.how_long = 10  # 10 seconds
        
        # Define circles (id, x, y, radius, color, highlighted_color)
        non_highlighted_color = (255, 255, 255)
        highlighted_color = (255, 0, 0)
        
        self.circles = [
            {"id": 0, "pos": (100, 100), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
            {"id": 1, "pos": (200, 200), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
            {"id": 2, "pos": (300, 150), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
            {"id": 3, "pos": (400, 300), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
            {"id": 4, "pos": (500, 100), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
            {"id": 5, "pos": (600, 200), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
            {"id": 6, "pos": (300, 400), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
            {"id": 7, "pos": (700, 500), "radius": 20, "color": non_highlighted_color, "highlight": highlighted_color},
        ]
        for c in self.circles:
            c["pos"] = (c["pos"][0]/800*self.manager.screen_width, c["pos"][1]/600*(self.manager.screen_height-200))

        # Keep track of which circle is currently highlighted
        self.active_circle_id = None

        # Generate invisible buttons
        self.forward_button = InvisibleButton(manager, default_button_type="forward", callback=self.go_forward)
        self.back_button = InvisibleButton(manager, default_button_type="back", callback=self.go_back)
        
        # Sounds
        self.positive_sound = load_sound("sounds/positive_sound.mp3")

        # Start time
        self.manager.shared_data["start_time"] = time.time()

        self.highlight_new_circle()

    def go_back(self):
        self.manager.switch_screen("EXPLANATION_SCREEN")

    def go_forward(self):
        self.manager.shared_data["end_reason"] = "early_abort"
        self.manager.shared_data["duration"] = int(time.time() - self.manager.shared_data["start_time"])
        self.manager.switch_screen("END_OF_GAME_SCREEN")
        
    def highlight_new_circle(self):
        # Choose a random circle other than the currently active one
        possible_ids = [c["id"] for c in self.circles if c["id"] != self.active_circle_id]
        if not possible_ids:
            return
        self.active_circle_id = random.choice(possible_ids)

    def handle_event(self, event):
        # Delegate events to the invisible buttons
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)
        
        # Check if user clicked on a circle
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if user clicked on active circle
            mx, my = event.pos
            for circle in self.circles:
                if circle["id"] == self.active_circle_id:
                    cx, cy = circle["pos"]
                    if (mx - cx) ** 2 + (my - cy) ** 2 <= circle["radius"] ** 2:
                        # Correct circle pressed
                        if self.positive_sound:
                            self.positive_sound.play()

                        # Increment dot counter
                        self.manager.shared_data["dots_pressed"] += 1

                        # Log press event
                        press_time = time.time()
                        self.manager.shared_data["press_times"].append(
                            (press_time, self.active_circle_id)
                        )

                        # Turn back to original color & highlight new one
                        self.highlight_new_circle()

        # Check game end conditions each click
        self.check_game_end_condition()

    def check_game_end_condition(self):
        # Dots reached 20 (or similar value)
        if self.manager.shared_data["dots_pressed"] >= self.how_often_to_press_dots:
            self.manager.shared_data["end_reason"] = "20_reached"
            self.manager.shared_data["duration"] = int(time.time() - self.manager.shared_data["start_time"])
            self.manager.switch_screen("END_OF_GAME_SCREEN")
            return

        # 5 minutes have passed
        elapsed_time = time.time() - self.manager.shared_data["start_time"]
        if elapsed_time > self.how_long:  # 300 seconds
            self.manager.shared_data["end_reason"] = "timeout"
            self.manager.shared_data["duration"] = int(time.time() - self.manager.shared_data["start_time"])
            self.manager.switch_screen("END_OF_GAME_SCREEN")

    def update(self):
        pass

    def draw(self, surface):
        
        # Draw the background
        surface.blit(self.background, (0, 0))

        # Draw counter, frozen if the game has ended
        elapsed_time = int(time.time() - self.manager.shared_data["start_time"])
        if not self.manager.shared_data.get("end_reason"):
            render_text(surface, f"Dots: {self.manager.shared_data['dots_pressed']} - Time: {elapsed_time}s", self.manager.minimum_letter_size, (255, 255, 255), (10, 10))
        else:
            render_text(surface, f"Dots: {self.manager.shared_data['dots_pressed']}", self.manager.minimum_letter_size, (255, 255, 255), (10, 10))

        # Draw circles
        for circle in self.circles:
            color = circle["highlight"] if circle["id"] == self.active_circle_id else circle["color"]
            pygame.draw.circle(surface, color, circle["pos"], circle["radius"])

        # Debug: Draw debug rectangles to verify button placement
        if self.manager.debug: 
            self.back_button.draw_debug(surface)
            self.forward_button.draw_debug(surface)
            