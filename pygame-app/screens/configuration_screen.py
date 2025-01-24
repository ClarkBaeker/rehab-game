import pygame
import pygame_gui
import cv2
import numpy as np
from games.connect_dots import TouchDots
from screens.screen_interface import ScreenInterface


game_mode_mapping = {
    "Connect the Dots": TouchDots,
    "Circle the Dots": TouchDots,
}

level_mapping = {
    "Level 1": None,
    "Level 2": None,
    "level 3": None
}


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
            html_text="<b>Configuration</b>: Click 'Start Calibration' to define the 4 corners.<br>"
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

        # Dropdown to select game mode
        self.game_mode_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["Connect the Dots", "Circle the Dots"],
            starting_option="Connect the Dots",  # default
            relative_rect=pygame.Rect(50, 320, 180, 30),
            manager=self.ui_manager,
        )

        self.level_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["Level 1", "Level 2", "Level 3"],
            starting_option="Level 1", #default
            relative_rect=pygame.Rect(50, 380, 180, 30),
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
        # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        #     if self.back_button_rect.collidepoint(event.pos):
        #         # Save the chosen input mode
        #         self.manager.shared_data["input_mode"] = self.input_mode_dropdown.selected_option[0]
        #         print(self.manager.shared_data["input_mode"])
        #         self.manager.switch_screen("HOME_SCREEN")

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
                print(self.manager.shared_data["input_mode"])
                # Save the chosen game
                self.manager.shared_data["game_mode"] = (
                    self.game_mode_dropdown.selected_option[0]
                )
                print(self.manager.shared_data["game_mode"])
                selected_game_class = game_mode_mapping.get(
                    self.game_mode_dropdown.selected_option[0], TouchDots
                )

                selected_level = level_mapping.get(
                    self.level_dropdown.selected_option[0]
                )
                # safe selected level
                #self.manager.level = selected_level(self.manager)

                self.manager.game = selected_game_class(self.manager)
                self.manager.switch_screen("HOME_SCREEN")

    def update(self):
        super().update()
        time_delta = self.manager.clock.get_time() / 1000.0
        self.ui_manager.update(time_delta)

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.background, (0, 0))

        # if self.manager.debug:
        #     pygame.draw.rect(surface, (255, 0, 0), self.back_button_rect, 2)

        self.ui_manager.draw_ui(surface)

    def on_exit(self):
        """
        This must be defined to satisfy the abstract method in ScreenInterface.
        """
        super().on_exit()
        # Do any additional cleanup if needed

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

        print("Calibration started. Click 4 corners in the live feed.")

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
        print("Calibration completed successfully.")


# import pygame
# import pygame_gui
# import cv2
# import numpy as np
# import time
# from screens.screen_interface import ScreenInterface


# class ConfigurationScreen(ScreenInterface):
#     def __init__(self, manager):
#         """
#         manager.shared_data will hold:
#             - "transform_matrix": The perspective transform (once calibrated)
#             - "input_mode": "mouse" or "finger"
#         """
#         # super().__init__(manager)

#         # self.background = pygame.image.load(
#         #     "images/start.png"
#         # ).convert()

#         self.ui_manager = pygame_gui.UIManager((manager.screen_width, manager.screen_height))

#         # Background or instructions label
#         self.title_label = pygame_gui.elements.UITextBox(
#             relative_rect=pygame.Rect(50, 50, manager.screen_width - 100, 100),
#             html_text="<b>Configuration</b>: Click 'Start Calibration' to define the 4 corners.<br>"
#                     "Then choose whether to use Mouse or Finger input in the Game Screen.",
#             manager=self.ui_manager
#         )

#         # Button to start corner calibration
#         self.calibration_button = pygame_gui.elements.UIButton(
#             relative_rect=pygame.Rect(50, 200, 180, 40),
#             text="Start Calibration",
#             manager=self.ui_manager
#         )

#         # Toggle between mouse or finger
#         self.input_mode_dropdown = pygame_gui.elements.UIDropDownMenu(
#             options_list=["mouse", "finger"],
#             starting_option="mouse",  # default
#             relative_rect=pygame.Rect(50, 260, 180, 30),
#             manager=self.ui_manager
#         )

#         # Button to return to home or explanation screen
#         self.back_button = pygame_gui.elements.UIButton(
#             relative_rect=pygame.Rect(50, manager.screen_height - 60, 100, 40),
#             text="Back",
#             manager=self.ui_manager
#         )

#     def on_enter(self):
#         super().on_enter()

#     def handle_event(self, event, time_delta=1):
#         self.ui_manager.process_events(event)

#         if event.type == pygame_gui.UI_BUTTON_PRESSED:
#             if event.ui_element == self.calibration_button:
#                 # Launch the corner calibration routine
#                 self.calibrate_corners()
#             elif event.ui_element == self.back_button:
#                 # Save the chosen input mode
#                 self.manager.shared_data["input_mode"] = self.input_mode_dropdown.selected_option
#                 self.manager.switch_screen("HOME_SCREEN")

#     def update(self): # , time_delta):
#         self.ui_manager.update(1) # time_delta)
#         # super().update()

#     def on_exit(self):
#         super().on_exit()

#     def draw(self, surface):
#         surface.fill((200, 200, 200))
#         self.ui_manager.draw_ui(surface)

#     def calibrate_corners(self):
#         """
#         Use OpenCV to capture from the webcam and let the user click 4 corners in the live feed.
#         This blocks until calibration is done. The result is stored in manager.shared_data["transform_matrix"].
#         """
#         cap = cv2.VideoCapture(0)  # open webcam 0
#         if not cap.isOpened():
#             print("Unable to open webcam.")
#             return

#         clicked_points = []

#         # We define a callback to capture mouse clicks on the live window
#         def on_mouse(event, x, y, flags, param):
#             if event == cv2.EVENT_LBUTTONDOWN:
#                 clicked_points.append((x, y))
#                 print(f"Clicked point: {x}, {y}")

#         cv2.namedWindow("Calibration")
#         cv2.setMouseCallback("Calibration", on_mouse)

#         print("Calibration started: click 4 corners in the live feed...")

#         # Loop until we have 4 points or user presses ESC
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             # Draw the clicks so far
#             for i, (cx, cy) in enumerate(clicked_points):
#                 cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
#                 cv2.putText(frame, str(i+1), (cx+5, cy-5),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

#             cv2.imshow("Calibration", frame)
#             key = cv2.waitKey(1)
#             if key == 27:  # ESC to cancel
#                 break
#             if len(clicked_points) == 4:
#                 # We got our 4 corners
#                 break

#         cap.release()
#         cv2.destroyWindow("Calibration")

#         if len(clicked_points) < 4:
#             print("Calibration aborted or incomplete.")
#             return

#         # Convert to float32
#         src_pts = np.float32(clicked_points)

#         # Destination points (corners in the game coordinate system).
#         # For an 800x600 game, define corners in the same logical order.
#         # (Top-left, top-right, bottom-right, bottom-left) or whichever consistent order you prefer.
#         dst_pts = np.float32([
#             [0, 0],
#             [self.manager.screen_width, 0],
#             [self.manager.screen_width, self.manager.screen_height],
#             [0, self.manager.screen_height]
#         ])

#         # Compute perspective transform matrix
#         M = cv2.getPerspectiveTransform(src_pts, dst_pts)
#         self.manager.shared_data["transform_matrix"] = M
#         print("Calibration done. Matrix stored in shared_data['transform_matrix'].")
