import pygame


class InvisibleButton:
    def __init__(self, manager, default_button_type="", rect=None, callback=None):
        """
        Initialize an invisible button.

        :param rect: pygame.Rect defining the button's clickable area.
        :param callback: Function to call when the button is clicked.
        """
        # Define button areas (matching the arrow locations in the image)
        if rect:
            self.rect = rect
        else:
            default_button_width = 400
            default_button_height = 250
            if default_button_type == "back":
                self.rect = pygame.Rect(
                    0,
                    manager.screen_height - default_button_height,
                    default_button_width,
                    default_button_height,
                )  # Bottom-left arrow
            if default_button_type == "forward":
                self.rect = pygame.Rect(
                    manager.screen_width - default_button_width,
                    manager.screen_height - default_button_height,
                    default_button_width,
                    default_button_height,
                )

        self.callback = callback

    def handle_event(self, event):
        """
        Handle mouse click events.

        :param event: A Pygame event object.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()

    def draw_debug(self, surface, color=(255, 0, 0), thickness=1):
        """
        Optional: Draw the button area for debugging purposes.

        :param surface: The Pygame surface to draw on.
        :param color: The color of the debug rectangle.
        :param thickness: The thickness of the rectangle lines.
        """
        pygame.draw.rect(surface, color, self.rect, thickness)
