import pygame
import pygame_gui
import cv2
import numpy as np
from screens.screen_interface import ScreenInterface


class ConfigurationScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        # Example background
        self.background = pygame.Surface((manager.screen_width, manager.screen_height))
        self.background.fill((200, 200, 200))

        # UI manager for managing GUI elements
        self.ui_manager = pygame_gui.UIManager(
            (manager.screen_width, manager.screen_height)
        )

        # Title text
        self.title_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(50, 50, manager.screen_width - 100, 100),
            html_text="<b>Configuration</b>: Click 'Start Calibration' to precisely define the 4 corners of blackboard for finger tracking.<br>"
            "Then choose whether to use Mouse or Finger input in the Game Screen.",
            manager=self.ui_manager,
        )

        # Button to start corner calibration
        self.calibration_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 200, 180, 40),
            text="Start Calibration",
            manager=self.ui_manager,
        )

        # Dropdown to select input mode
        self.input_mode_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["mouse", "finger"],
            starting_option="finger",  # default
            relative_rect=pygame.Rect(50, 260, 180, 30),
            manager=self.ui_manager,
        )

        # Invisible back button area (instead of a pygame_gui button)
        # self.back_button_rect = pygame.Rect(50, manager.screen_height - 60, 100, 40)
        # Confirmation button
        self.back_button_rect = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                manager.screen_height - 300, manager.screen_height - 100, 200, 50
            ),
            text="Confirm",
            manager=self.ui_manager,
        )

    def on_enter(self):
        super().on_enter()

    def handle_event(self, event):

        # Let the UI manager handle GUI events (e.g. calibration button)
        self.ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.calibration_button:
                self.calibrate_corners()
            if event.ui_element == self.back_button_rect:
                # Save the chosen input mode
                self.manager.shared_data["input_mode"] = (
                    self.input_mode_dropdown.selected_option[0]
                )
                print(f"{self.manager.shared_data['input_mode']} input mode selected.")
                self.manager.switch_screen("HOME_SCREEN")

    def update(self):
        super().update()
        time_delta = self.manager.clock.get_time() / 1000.0
        self.ui_manager.update(time_delta)

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.background, (0, 0))
        self.ui_manager.draw_ui(surface)

    def on_exit(self):
        super().on_exit()

    def calibrate_corners(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        clicked_points = []

        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked_points.append((x, y))
                print(f"Clicked point: {x}, {y}")

        cv2.namedWindow("Calibration")
        cv2.setMouseCallback("Calibration", on_mouse)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Display clicks so far
            for i, (cx, cy) in enumerate(clicked_points):
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    str(i + 1),
                    (cx + 5, cy - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 0),
                    2,
                )

            cv2.imshow("Calibration", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC to cancel
                break
            if len(clicked_points) == 4:
                break

        cap.release()
        cv2.destroyWindow("Calibration")

        if len(clicked_points) < 4:
            print("Calibration aborted or incomplete.")
            return

        src_pts = np.float32(clicked_points)
        dst_pts = np.float32(
            [
                [0, 0],
                [self.manager.screen_width, 0],
                [self.manager.screen_width, self.manager.screen_height],
                [0, self.manager.screen_height],
            ]
        )

        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        self.manager.shared_data["transform_matrix"] = M
        self.manager.shared_data["calibration_points"] = clicked_points
