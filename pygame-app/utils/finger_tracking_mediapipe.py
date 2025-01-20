import cv2
import mediapipe as mp
import numpy as np

class FingerTracker:
    def __init__(self, transform_matrix, screen_width, screen_height):
        self.transform_matrix = transform_matrix
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_finger_position(self, frame):
        """
        Returns the mapped (x, y) in game coordinates of the index finger tip, or None if not found.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Index finger tip is landmark #8
                index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Landmark coordinates are normalized [0,1], so we map to pixel coords
                height, width, _ = frame.shape
                px = int(index_finger_tip.x * width)
                py = int(index_finger_tip.y * height)

                # Now apply perspective transform if we have it
                if self.transform_matrix is not None:
                    # perspectiveTransform expects shape (N, 1, 2)
                    points = np.array([[[px, py]]], dtype='float32')
                    mapped = cv2.perspectiveTransform(points, self.transform_matrix)
                    mapped_x, mapped_y = mapped[0, 0, 0], mapped[0, 0, 1]

                    # Optionally clamp or scale to screen boundaries
                    mapped_x = max(0, min(self.screen_width, mapped_x))
                    mapped_y = max(0, min(self.screen_height, mapped_y))

                    return (mapped_x, mapped_y)

        return None
