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
        print(self.level)

        # Define the size of the game screen
        self.game_screen_width = self.manager.screen_width * 1 / 2
        self.game_screen_height = self.manager.screen_height * 5 / 6

        # Dots are drawn in percent from the center of the screen
        dist_x = 12  # horizontal distance between dots, in percent. Assumption: Non-even number
        dist_y = (
            12  # vertical distance between dots, in percent. Assumption: Even number
        )

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
                c["pos"][0] / 100 * self.manager.screen_width
                + self.manager.screen_width / 2,
                c["pos"][1] / 100 * (self.manager.screen_height)
                + self.manager.screen_height / 2,
            )
        self.active_dot_id: int = None
        self.maximum_duration = 5 * 60  # in seconds
        if self.level == "Level 1":
            self.order = [9, 10, 11]

        if self.level == "Level 2":
            self.order = [9, 8, 5, 0]

        if self.level == "Level 3":
            self.order = [9, 7, 5, 2]

        self.how_often_to_press_dots = len(self.order)
        self.maximum_duration = 3 * 60
        self.current_idx = 0

        self.positive_sound = load_sound("sounds/positive_sound.mp3")

    def start(self):
        super().start()
        self.manager.shared_data["dots_pressed"] = (
            0  # will store the number of dots pressed
        )
        self.manager.shared_data["press_times"] = []  # will store (time_stamp, dot_id)
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
                self._check_dot_collision(mx, my)
            self._check_game_end_condition()

    def update(self, finger_x, finger_y):
        super().update()
        self._check_dot_collision(finger_x, finger_y)
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

    def _highlight_new_dot(self):
        possible_ids = [
            c["id"]
            for c in self.dots
            if c["id"] != self.active_dot_id
            # and c["id"] in [0, 1]  # change this back after all leds are connected
        ]
        if not possible_ids:
            return
        self.active_dot_id = random.choice(possible_ids)
        self.manager.send_message(
            "BoardESP", {"command": "turn_on", "led_id": self.active_dot_id}
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
                    self.manager.shared_data.setdefault("press_times", [])
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
            self.manager.shared_data["duration"] = int(
                time.time() - self.manager.shared_data["start_time"]
            )
            self.end_game()
            return

        elapsed_time = time.time() - self.manager.shared_data["start_time"]
        if elapsed_time > self.maximum_duration:
            self.manager.shared_data["end_reason"] = "timeout"
            self.manager.shared_data["duration"] = int(
                time.time() - self.manager.shared_data["start_time"]
            )
            self.end_game()
