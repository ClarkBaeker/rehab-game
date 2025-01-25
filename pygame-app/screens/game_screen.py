import pygame
import time
import cv2

from screens.screen_interface import ScreenInterface
from utils.invisible_button import InvisibleButton

WINDOW_NAME = "Finger Tracking Window"

class GameScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        # Background image
        self.background = pygame.image.load("images/game.png").convert()

        # Navigation buttons
        self.forward_button = InvisibleButton(
            manager, default_button_type="forward", callback=self.go_forward
        )
        self.back_button = InvisibleButton(
            manager, default_button_type="back", callback=self.go_back
        )

        # Finger tracking
        self.cap = None
        self.finger_tracker = None
        self.finger_x = None
        self.finger_y = None

        # Game screen configuration
        self.rescale_to_game_screen = True
        self.border_width = 8
        self.game_screen_width = None
        self.game_screen_height = None
        self.x_offset = None
        self.y_offset = None

    def on_enter(self):
        """
        Called when the screen becomes active.
        - Initializes game variables
        - Logs start of new game
        - Sets up finger tracking if needed
        """
        super().on_enter()
        
        # Reset shared_data, such that the game can be restarted 
        self.manager.game.game_ended = False
        self.manager.shared_data["start_time"] = None
        self.manager.shared_data["end_reason"] = None
        self.manager.shared_data["feedback"] = None
        
        # Log a new game
        self.manager.logger.start_new_game()

        # Fetch dimensions from the current game
        self.sync_game_screen_dimensions()

        # Start the game logic in manager.game
        self.manager.game.start()

        # Handle input mode and calibration
        self.input_mode = self.manager.shared_data.get("input_mode", "mouse")
        self.transform_matrix = self.manager.shared_data.get("transform_matrix")
        self.calibration_points = self.manager.shared_data.get("calibration_points", [])
        
        if self.input_mode == "finger":
            self.initialize_finger_tracking()

    def sync_game_screen_dimensions(self):
        """
        Syncs the local game screen dimensions (border, offsets) with
        whatever the active game (`manager.game`) is using.
        """
        # In case the game object sets these attributes:
        self.game_screen_width = getattr(self.manager.game, 'game_screen_width', self.manager.screen_width / 2)
        self.game_screen_height = getattr(self.manager.game, 'game_screen_height', self.manager.screen_height * 5/6)

        self.x_offset = (self.manager.screen_width - self.game_screen_width) / 2
        # Push the game screen down so lower boundary isn’t visible
        self.y_offset = self.manager.screen_height - self.game_screen_height + self.border_width

    def initialize_finger_tracking(self):
        """
        Sets up the OpenCV webcam capture and initializes a FingerTracker.
        """
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
            # Configure the OpenCV window
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 640, 480)

    def go_back(self):
        """
        Called when the back button is pressed.
        Ends the game and switches to explanation screen.
        """
        self.manager.game.end_game()
        self.manager.switch_screen("EXPLANATION_SCREEN")

    def go_forward(self):
        """
        Called when the forward button is pressed.
        Ends the game early and moves to the end-of-game screen.
        """
        self.manager.game.end_game()
        self.manager.shared_data["end_reason"] = "early_abort"
        self.manager.shared_data["duration"] = int(
            time.time() - self.manager.shared_data["start_time"]
        )
        self.manager.switch_screen("END_OF_GAME_SCREEN")

    def handle_event(self, event):
        """
        Handles user interactions (buttons, etc.).
        Passes events to the underlying game as well.
        """
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)
        self.manager.game.handle_event(event)

    def update(self):
        """
        Called every frame to update game state.
        Handles finger tracking input if in finger mode.
        """
        super().update()
        if self.input_mode == "finger" and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                self.process_finger_tracking(frame)

    def process_finger_tracking(self, frame):
        """
        Reads the current frame for finger tracking, updates the game
        with finger positions, and displays an OpenCV window.
        """
        if not self.finger_tracker:
            # If FingerTracker is not set, do nothing
            return  
        finger_data = self.finger_tracker.get_finger_position(frame)
        if finger_data:
            mapped_x, mapped_y, cam_x, cam_y = finger_data
            if self.rescale_to_game_screen:
                mapped_x = self.rescale_x(mapped_x)
                mapped_y = self.rescale_y(mapped_y)

            # Update the game logic with these coordinates
            self.finger_x, self.finger_y = mapped_x, mapped_y
            self.manager.game.update(self.finger_x, self.finger_y)

            # Draw a red circle in the camera feed where the finger is
            cv2.circle(frame, (cam_x, cam_y), 10, (0, 0, 255), -1)
            
        # Even if there's no finger, frame and vido will still be shown
        self.draw_calibration_rectangle(frame)
        cv2.imshow(WINDOW_NAME, frame)
        cv2.waitKey(1)

        # If the game has ended, switch screens
        if self.manager.game.game_ended:
            self.manager.switch_screen("END_OF_GAME_SCREEN")

    def draw_calibration_rectangle(self, frame):
        """
        Draws a rectangle connecting the 4 calibration points (if present).
        """
        if len(self.calibration_points) == 4:
            for i in range(4):
                pt1 = self.calibration_points[i]
                pt2 = self.calibration_points[(i + 1) % 4]
                cv2.line(frame, pt1, pt2, (255, 255, 0), 2)

    def draw(self, surface):
        """
        Renders everything onto the Pygame surface:
        - Background
        - The underlying game
        - Brown rectangle border
        - Finger cursor (if in finger mode)
        - Debug outlines for back/forward buttons
        """
        super().draw(surface)
        surface.blit(self.background, (0, 0))

        # Draw the active game
        self.manager.game.draw(surface)

        # Brown rectangle border around the game screen
        if self.rescale_to_game_screen and self.game_screen_width and self.game_screen_height:
            brown_color = (139, 69, 19)
            pygame.draw.rect(
                surface,
                brown_color,
                (self.x_offset, self.y_offset, self.game_screen_width, self.game_screen_height),
                width=self.border_width
            )

        # Draw finger position if in finger mode
        if self.input_mode == "finger" and self.finger_x is not None and self.finger_y is not None:
            pygame.draw.circle(surface, (255, 0, 0), (int(self.finger_x), int(self.finger_y)), 10)
            self.manager.logger.append_finger_data(self.finger_x, self.finger_y)

        # Debug outlines for buttons
        if self.manager.debug:
            self.back_button.draw_debug(surface)
            self.forward_button.draw_debug(surface)

    def rescale_x(self, x):
        """
        Scale the raw x-coordinate to fit the game screen area.
        """
        if not self.game_screen_width:
            return x
        return (x / self.manager.screen_width) * self.game_screen_width + self.x_offset

    def rescale_y(self, y):
        """
        Scale the raw y-coordinate to fit the game screen area.
        """
        if not self.game_screen_height:
            return y
        return (y / self.manager.screen_height) * self.game_screen_height + self.y_offset

    def on_exit(self):
        """
        Cleans up resources when leaving this screen.
        Closes OpenCV windows and releases the webcam capture.
        """
        super().on_exit()
        if self.cap is not None:
            cv2.destroyAllWindows()  # Close any OpenCV windows
            cv2.waitKey(1)          # Allow the OS time to process the close
            self.cap.release()
