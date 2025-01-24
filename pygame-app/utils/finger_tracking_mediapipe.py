import cv2
import mediapipe as mp
import numpy as np

class FingerTracker:
    def __init__(self, transform_matrix, screen_width, screen_height, calibration_points=None):
        """
        :param transform_matrix: The perspective transform matrix from calibration.
        :param screen_width: Width of the Pygame window (for mapped coords).
        :param screen_height: Height of the Pygame window (for mapped coords).
        :param calibration_points: The original 4 clicked corners in camera space (optional).
        """
        self.transform_matrix = transform_matrix
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.calibration_points = calibration_points  # e.g. [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_finger_position(self, frame):
        """
        Returns a tuple of:
            (mapped_x, mapped_y, camera_x, camera_y)
        or None if no finger found.

        mapped_x, mapped_y: The finger position in GAME coordinates.
        camera_x, camera_y: The finger position in the camera frame's pixel coords.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Index finger tip is landmark #8
                index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

                height, width, _ = frame.shape
                camera_x = int(index_finger_tip.x * width)
                camera_y = int(index_finger_tip.y * height)

                if self.transform_matrix is not None:
                    # perspectiveTransform expects shape (N, 1, 2)
                    points = np.array([[[camera_x, camera_y]]], dtype='float32')
                    mapped = cv2.perspectiveTransform(points, self.transform_matrix)
                    mapped_x, mapped_y = mapped[0, 0, 0], mapped[0, 0, 1]

                    # Clamp to screen boundaries
                    mapped_x = max(0, min(self.screen_width, mapped_x))
                    mapped_y = max(0, min(self.screen_height, mapped_y))
                else:
                    # If no transform, just position in top-left corner
                    mapped_x, mapped_y = camera_x, camera_y

                return (mapped_x, mapped_y, camera_x, camera_y)

        return None
