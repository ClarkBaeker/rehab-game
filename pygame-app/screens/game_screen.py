import pygame
import time
from screens.screen_interface import ScreenInterface
from utils.utils import render_text, load_sound
from utils.invisible_button import InvisibleButton
import random
import cv2

class GameScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        self.background = pygame.image.load("images/game.png").convert()

        self.how_often_to_press_dots = 20
        if self.manager.debug:
            self.how_often_to_press_dots = 3

        self.how_long = 5 * 60  # in seconds
        if self.manager.debug:
            self.how_long = 10

        non_highlighted_color = (255, 255, 255)
        highlighted_color = (255, 0, 0)

        self.circles = [
            {"id":0, "pos":(100,100), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
            {"id":1, "pos":(200,200), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
            {"id":2, "pos":(300,150), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
            {"id":3, "pos":(400,300), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
            {"id":4, "pos":(500,100), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
            {"id":5, "pos":(600,200), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
            {"id":6, "pos":(300,400), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
            {"id":7, "pos":(700,500), "radius":20, "color":non_highlighted_color, "highlight":highlighted_color},
        ]

        for c in self.circles:
            c["pos"] = (
                c["pos"][0] / 800 * self.manager.screen_width,
                c["pos"][1] / 600 * (self.manager.screen_height - 200),
            )

        self.active_circle_id = None
        self.highlight_new_circle()

        self.forward_button = InvisibleButton(
            manager, default_button_type="forward", callback=self.go_forward
        )
        self.back_button = InvisibleButton(
            manager, default_button_type="back", callback=self.go_back
        )

        self.positive_sound = load_sound("sounds/positive_sound.mp3")

        # Variables for finger tracking
        self.cap = None
        self.finger_tracker = None
        self.finger_x = None
        self.finger_y = None

    def on_enter(self):
        self.manager.shared_data["start_time"] = time.time()
        self.manager.shared_data["dots_pressed"] = 0
        self.manager.shared_data["end_reason"] = None

        self.highlight_new_circle()

        self.input_mode = self.manager.shared_data.get("input_mode", "mouse")
        self.transform_matrix = self.manager.shared_data.get("transform_matrix", None)
        # Load the 4 calibration corner points if you stored them
        self.calibration_points = self.manager.shared_data.get("calibration_points", [])

        if self.input_mode == "finger":
            print("is in finger mode")
            from utils.finger_tracking_mediapipe import FingerTracker
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Warning: Could not open webcam.")
                self.cap = None
            else:
                print("Tracking finger...")
                self.finger_tracker = FingerTracker(
                    transform_matrix=self.transform_matrix,
                    screen_width=self.manager.screen_width,
                    screen_height=self.manager.screen_height,
                    calibration_points=self.calibration_points
                )
                cv2.namedWindow("Finger Tracking Window", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Finger Tracking Window", 640, 480)

        super().on_enter()

    def go_back(self):
        self.manager.switch_screen("EXPLANATION_SCREEN")

    def go_forward(self):
        self.manager.shared_data["end_reason"] = "early_abort"
        self.manager.shared_data["duration"] = int(
            time.time() - self.manager.shared_data["start_time"]
        )
        self.manager.switch_screen("END_OF_GAME_SCREEN")

    def highlight_new_circle(self):
        possible_ids = [c["id"] for c in self.circles if c["id"] != self.active_circle_id]
        if not possible_ids:
            return
        self.active_circle_id = random.choice(possible_ids)

    def handle_event(self, event):
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)

        # Mouse-based circle collision
        if self.input_mode == "mouse":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.check_circle_collision(mx, my)

        self.check_game_end_condition()

    def check_circle_collision(self, x, y):
        for circle in self.circles:
            if circle["id"] == self.active_circle_id:
                cx, cy = circle["pos"]
                if (x - cx) ** 2 + (y - cy) ** 2 <= circle["radius"] ** 2:
                    if self.positive_sound:
                        self.positive_sound.play()

                    self.manager.shared_data["dots_pressed"] += 1
                    press_time = time.time()
                    self.manager.shared_data.setdefault("press_times", [])
                    self.manager.shared_data["press_times"].append(
                        (press_time, self.active_circle_id)
                    )
                    self.highlight_new_circle()

    def update(self):
        super().update()

        if self.input_mode == "finger" and self.cap is not None:
            ret, frame = self.cap.read()
            if ret and self.finger_tracker:
                # Get the mapped finger coords + camera coords
                finger_data = self.finger_tracker.get_finger_position(frame)
                if finger_data:
                    mapped_x, mapped_y, cam_x, cam_y = finger_data
                    self.finger_x, self.finger_y = mapped_x, mapped_y
                    # Check collision with the active circle (in game coords)
                    self.check_circle_collision(self.finger_x, self.finger_y)
                    self.check_game_end_condition() # TODO

                    # Draw the calibration rectangle if there are calibration points
                    if len(self.calibration_points) == 4:
                        for i in range(4):
                            pt1 = self.calibration_points[i]
                            pt2 = self.calibration_points[(i+1) % 4]
                            cv2.line(frame, pt1, pt2, (255, 255, 0), 2)

                    # Draw the finger position in camera coords
                    cv2.circle(frame, (cam_x, cam_y), 10, (0, 0, 255), -1)
                

                    # Show the result in a separate window
                    cv2.imshow("Finger Tracking Window", frame)
                    cv2.waitKey(10)
                    # print("Showing frame now...")

    def check_game_end_condition(self):
        if self.manager.shared_data["dots_pressed"] >= self.how_often_to_press_dots:
            self.manager.shared_data["end_reason"] = "20_reached"
            self.manager.shared_data["duration"] = int(
                time.time() - self.manager.shared_data["start_time"]
            )
            self.manager.switch_screen("END_OF_GAME_SCREEN")
            # self.cleanup()
            self.on_exit()
            return

        elapsed_time = time.time() - self.manager.shared_data["start_time"]
        if elapsed_time > self.how_long:
            self.manager.shared_data["end_reason"] = "timeout"
            self.manager.shared_data["duration"] = int(
                time.time() - self.manager.shared_data["start_time"]
            )
            self.manager.switch_screen("END_OF_GAME_SCREEN")
            # self.cleanup()
            self.on_exit()


    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.background, (0, 0))
        
        # If finger mode, draw a red "cursor" on the game screen
        if self.input_mode == "finger" and self.finger_x is not None and self.finger_y is not None:
            pygame.draw.circle(surface, (255, 0, 0), (int(self.finger_x), int(self.finger_y)), 10)

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

        # Draw circles
        for circle in self.circles:
            color = (
                circle["highlight"] if circle["id"] == self.active_circle_id else circle["color"]
            )
            pygame.draw.circle(surface, color, circle["pos"], circle["radius"])

        # Debug
        if self.manager.debug:
            self.back_button.draw_debug(surface)
            self.forward_button.draw_debug(surface)

    def on_exit(self):
        if self.cap is not None:
            self.cap.release()
            cv2.destroyWindow("Finger Tracking Window")
        super().on_exit()