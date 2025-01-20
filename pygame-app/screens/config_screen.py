import pygame
import pygame_gui
import cv2
import numpy as np
import time

class ConfigScreen:
    def __init__(self, manager):
        """
        manager.shared_data will hold:
          - "transform_matrix": The perspective transform (once calibrated)
          - "input_mode": "mouse" or "finger"
        """
        self.manager = manager
        self.ui_manager = pygame_gui.UIManager((manager.screen_width, manager.screen_height))

        # Background or instructions label
        self.title_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(50, 50, manager.screen_width - 100, 100),
            html_text="<b>Configuration</b>: Click 'Start Calibration' to define the 4 corners.<br>"
                      "Then choose whether to use Mouse or Finger input in the Game Screen.",
            manager=self.ui_manager
        )

        # Button to start corner calibration
        self.calibration_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 200, 180, 40),
            text="Start Calibration",
            manager=self.ui_manager
        )

        # Toggle between mouse or finger
        self.input_mode_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["mouse", "finger"],
            starting_option="mouse",  # default
            relative_rect=pygame.Rect(50, 260, 180, 30),
            manager=self.ui_manager
        )

        # Button to return to home or explanation screen
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, manager.screen_height - 60, 100, 40),
            text="Back",
            manager=self.ui_manager
        )

    def handle_event(self, event, time_delta):
        self.ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.calibration_button:
                # Launch the corner calibration routine
                self.calibrate_corners()
            elif event.ui_element == self.back_button:
                # Save the chosen input mode
                self.manager.shared_data["input_mode"] = self.input_mode_dropdown.selected_option
                self.manager.switch_screen("HOME_SCREEN")

    def update(self, time_delta):
        self.ui_manager.update(time_delta)

    def draw(self, surface):
        surface.fill((200, 200, 200))
        self.ui_manager.draw_ui(surface)

    def calibrate_corners(self):
        """
        Use OpenCV to capture from the webcam and let the user click 4 corners in the live feed.
        This blocks until calibration is done. The result is stored in manager.shared_data["transform_matrix"].
        """
        cap = cv2.VideoCapture(0)  # open webcam 0
        if not cap.isOpened():
            print("Unable to open webcam.")
            return

        clicked_points = []

        # We define a callback to capture mouse clicks on the live window
        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked_points.append((x, y))
                print(f"Clicked point: {x}, {y}")

        cv2.namedWindow("Calibration")
        cv2.setMouseCallback("Calibration", on_mouse)

        print("Calibration started: click 4 corners in the live feed...")

        # Loop until we have 4 points or user presses ESC
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Draw the clicks so far
            for i, (cx, cy) in enumerate(clicked_points):
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(frame, str(i+1), (cx+5, cy-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            cv2.imshow("Calibration", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC to cancel
                break
            if len(clicked_points) == 4:
                # We got our 4 corners
                break

        cap.release()
        cv2.destroyWindow("Calibration")

        if len(clicked_points) < 4:
            print("Calibration aborted or incomplete.")
            return

        # Convert to float32
        src_pts = np.float32(clicked_points)

        # Destination points (corners in the game coordinate system).
        # For an 800x600 game, define corners in the same logical order.
        # (Top-left, top-right, bottom-right, bottom-left) or whichever consistent order you prefer.
        dst_pts = np.float32([
            [0, 0],
            [self.manager.screen_width, 0],
            [self.manager.screen_width, self.manager.screen_height],
            [0, self.manager.screen_height]
        ])

        # Compute perspective transform matrix
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        self.manager.shared_data["transform_matrix"] = M
        print("Calibration done. Matrix stored in shared_data['transform_matrix'].")
