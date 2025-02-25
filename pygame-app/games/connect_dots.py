import random
import time

import pygame
from games.game_interface import GameInterface
from utils.utils import load_sound, render_text

NON_HIGHLIGHTED_COLOR = (255, 255, 255)
HIGHLIGHTED_COLOR = (255, 0, 0)


class TouchDots(GameInterface):

    def __init__(self, manager):
        super().__init__(manager)
        self.level = self.manager.shared_data["level"]

        # Define the size of the game screen
        scaler = 50
        self.game_screen_width = 12 * scaler
        self.game_screen_height = 12 * scaler

        # Dots are drawn in percent from the center of the screen
        dist_x = 1 / 3  # horizontal distance between dots, as ratio
        dist_y = 1 / 4  # vertical distance between dots, as ratio

        self.dots = [
            {
                "id": 0,
                "pos": (-dist_x, -3 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 1,
                "pos": (0, -3 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 2,
                "pos": (+dist_x, -3 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 3,
                "pos": (-dist_x, -1 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 4,
                "pos": (0, -1 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 5,
                "pos": (+dist_x, -1 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 6,
                "pos": (-dist_x, +1 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 7,
                "pos": (0, +1 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 8,
                "pos": (+dist_x, +1 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 9,
                "pos": (-dist_x, +3 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 10,
                "pos": (0, +3 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
            {
                "id": 11,
                "pos": (+dist_x, +3 / 2 * dist_y),
                "radius": 20,
                "color": NON_HIGHLIGHTED_COLOR,
                "highlight": HIGHLIGHTED_COLOR,
            },
        ]

        for c in self.dots:
            c["pos"] = (
                c["pos"][0] * self.game_screen_width + self.manager.screen_width / 2,
                c["pos"][1] * (self.game_screen_height)
                + self.manager.screen_height / 2,
            )

        if self.manager.shared_data["game_mode"] == "Connect the Dots":
            if self.level == "Level 1":
                self.order = [9, 10, 11, 6, 7, 8, 3, 4, 5, 0, 1, 2]

            if self.level == "Level 2":
                self.order = [9, 7, 5, 4, 3, 7, 11, 1, 9]

            if self.level == "Level 3":
                self.order = [9, 7, 5, 4, 3, 6, 9, 10, 11, 8, 5, 1, 3, 7, 11]

        elif self.manager.shared_data["game_mode"] == "Circle the Dots":
            if self.level == "Level 1":
                self.order = [7, 4, 8, 10, 6]

            if self.level == "Level 2":
                self.order = [7, 4, 8, 10, 6, 3, 1, 5, 11, 9]

            if self.level == "Level 3":
                self.order = [10, 7, 4, 0, 1, 2]

        self.active_dot_id: int = None
        self.maximum_duration = 5 * 60  # in seconds
        self.how_often_to_press_dots = len(self.order)
        self.current_idx = 0
        self.positive_sound = load_sound("sounds/positive_sound.mp3")
        self.shared_data = {
            "dots_pressed": 0,
            "press_times": [],
        }  # will store the number of dots pressed with times
        # Ensure clean start regarding game specific shared data
        self.rmv_shared_data()
        self.add_shared_data()

    def start(self):
        super().start()
        self.current_idx = 0
        self._highlight_next()
        self.manager.send_message(
            "KneeESP",
            {"command": "turn_on"},
        )

    def handle_event(self, event):
        super().handle_event(event)
        # Mouse-based dot collision
        if self.manager.shared_data["input_mode"] == "mouse":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.update(mx, my, check_collision=True)
            else:
                # Do not check collision, as the mouse is not pressed
                mx, my = pygame.mouse.get_pos()
                self.update(mx, my, check_collision=False)

    def update(self, pos_x, pos_y, check_collision=True):
        super().update()
        self.manager.logger.append_position_data(pos_x, pos_y)
        if check_collision:
            self._check_dot_collision(pos_x, pos_y)
            self._check_game_end_condition()

    def draw(self, surface):
        super().draw(surface)
        # Timer or final dots
        if not self.manager.shared_data.get("end_reason"):
            elapsed_time = int(time.time() - self.manager.shared_data["start_time"])
            render_text(
                surface,
                f"Dots: {self.manager.shared_data['dots_pressed']} - Time: {elapsed_time}s",
                self.manager.minimum_letter_size,
                (255, 255, 255),
                (10, 10),
            )
        else:
            render_text(
                surface,
                f"Dots: {self.manager.shared_data['dots_pressed']}",
                self.manager.minimum_letter_size,
                (255, 255, 255),
                (10, 10),
            )

        # Draw dots
        for dot in self.dots:
            color = (
                dot["highlight"] if dot["id"] == self.active_dot_id else dot["color"]
            )
            pygame.draw.circle(surface, color, dot["pos"], dot["radius"])

    def end_game(self):
        super().end_game()
        self.manager.send_message(
            "BoardESP",
            {"command": "turn_off", "led_id": self.active_dot_id},
        )
        self.manager.send_message(
            "KneeESP",
            {"command": "turn_off"},
        )

    def _highlight_next(self):
        if self.current_idx >= len(self.order):
            return

        self.active_dot_id = self.order[self.current_idx]

        self.manager.send_message(
            "BoardESP", {"command": "turn_on", "led_id": self.active_dot_id}
        )
        self.current_idx += 1

    def _check_dot_collision(self, x, y):
        for dot in self.dots:
            if dot["id"] == self.active_dot_id:
                cx, cy = dot["pos"]
                if (x - cx) ** 2 + (y - cy) ** 2 <= dot["radius"] ** 2:
                    if self.positive_sound:
                        self.positive_sound.play()

                    self.manager.shared_data["dots_pressed"] += 1
                    press_time = time.time()
                    self.manager.shared_data["press_times"].append(
                        (press_time, self.active_dot_id)
                    )
                    self.manager.send_message(
                        "BoardESP",
                        {"command": "turn_off", "led_id": self.active_dot_id},
                    )
                    self._highlight_next()
                    self._check_game_end_condition()

    def _check_game_end_condition(self):
        if self.manager.shared_data["dots_pressed"] >= self.how_often_to_press_dots:
            self.manager.shared_data["end_reason"] = "win"
            self.end_game()
            return

        elapsed_time = time.time() - self.manager.shared_data["start_time"]
        if elapsed_time > self.maximum_duration:
            self.manager.shared_data["end_reason"] = "timeout"
            self.end_game()
