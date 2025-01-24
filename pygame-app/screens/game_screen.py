import pygame
import time
from screens.screen_interface import ScreenInterface
from utils.invisible_button import InvisibleButton
import cv2

WINDOW_NAME = "Finger Tracking Window"

class GameScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        self.background = pygame.image.load("images/game.png").convert()

        self.forward_button = InvisibleButton(
            manager, default_button_type="forward", callback=self.go_forward
        )
        self.back_button = InvisibleButton(
            manager, default_button_type="back", callback=self.go_back
        )

        # Variables for finger tracking
        self.cap = None
        self.finger_tracker = None
        self.finger_x = None
        self.finger_y = None

    def on_enter(self):
        super().on_enter()
        self.manager.shared_data["end_reason"] = None

        self.manager.game.start()
        self.manager.logger.start_new_game()

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
                    calibration_points=self.calibration_points,
                )
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 640, 480)

    def go_back(self):
        self.manager.game.end_game()
        self.manager.switch_screen("EXPLANATION_SCREEN")

    def go_forward(self):
        self.manager.game.end_game()
        self.manager.shared_data["end_reason"] = "early_abort"
        self.manager.shared_data["duration"] = int(
            time.time() - self.manager.shared_data["start_time"]
        )
        self.manager.switch_screen("END_OF_GAME_SCREEN")

    def handle_event(self, event):
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)
        self.manager.game.handle_event(event)

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
                    self.manager.game.update(self.finger_x, self.finger_y)

                    # Draw the calibration rectangle if there are calibration points
                    if len(self.calibration_points) == 4:
                        for i in range(4):
                            pt1 = self.calibration_points[i]
                            pt2 = self.calibration_points[(i + 1) % 4]
                            cv2.line(frame, pt1, pt2, (255, 255, 0), 2)

                    # Draw the finger position in camera coords
                    cv2.circle(frame, (cam_x, cam_y), 10, (0, 0, 255), -1)

                    # Show the result in a separate window
                    cv2.imshow(WINDOW_NAME, frame)
                    cv2.waitKey(10)
                    if self.manager.game.game_ended:
                        self.manager.switch_screen("END_OF_GAME_SCREEN")
                    # print("Showing frame now...")

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.background, (0, 0))

        # If finger mode, draw a red "cursor" on the game screen and record the finger position
        if (
            self.input_mode == "finger"
            and self.finger_x is not None
            and self.finger_y is not None
        ):
            # Draw the finger position on the game screen
            pygame.draw.circle(
                surface, (255, 0, 0), (int(self.finger_x), int(self.finger_y)), 10
            )
            
            # Append data to the trajectory logger
            self.manager.logger.append_finger_data(self.finger_x, self.finger_y)

        self.manager.game.draw(surface)

        # Debug
        if self.manager.debug:
            self.back_button.draw_debug(surface)
            self.forward_button.draw_debug(surface)

    def on_exit(self):
        super().on_exit()
        if self.cap is not None:
            for i in range(1, 5):
                cv2.destroyAllWindows()
                cv2.waitKey(1)
            self.cap.release()
