import pygame
from screens.screen_interface import ScreenInterface
from utils.utils import render_text
from utils.invisible_button import InvisibleButton


class ExplanationConnectDots(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        # Load the background with arrows
        self.background = pygame.image.load("images/game.png").convert()


        self.screen_width = (
            1792  # >> images imported from canva: scaling of 0.93333333333
        )
        self.screen_height = 1008


        # Generate invisible buttons
        self.forward_button = InvisibleButton(
            manager, default_button_type="forward", callback=self.go_forward
        )
        self.back_button = InvisibleButton(
            manager, default_button_type="back", callback=self.go_back
        )

    def on_enter(self):
        super().on_enter()

    def go_back(self):
        self.manager.switch_screen("HOME_SCREEN")

    def go_forward(self):
        self.manager.switch_screen("GAME_SCREEN")

    def handle_event(self, event):  # , time_delta):
        # Delegate events to the invisible buttons
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)

    def update(self):
        super().update()



    def draw(self, surface):
        super().draw(surface)
        # Draw the background
        surface.blit(self.background, (0, 0))
        #surface.fill((255, 255, 255))

        # Font
        titleFont = pygame.font.Font(None, 150)
        textFont = pygame.font.Font(None, 60)
        white = (255, 255, 255)


        # Render the title and text
        title_surface = titleFont.render("Punkte verbinden", True, white)  # True enables anti-aliasing
        text_surface = """Willkommen! 
                        Stellen Sie sich vor die Tafel und 
                        positionieren Sie Ihre Füße auf den Markierungen.
                       Nehmen Sie ein Stück Kreide in die rechte Hand. 
                       Ihre Aufgabe ist es, 
                       nacheinander die aufleuchtenden Punkte miteinander zu verbinden.
                       Viel Spaß!"""

        # Get the rectangles for positioning
        x, y = 2, 300
        title_rect = title_surface.get_rect(center=(self.screen_width // x, 100))  # Centered at the top

        surface.blit(title_surface, title_rect)
        #surface.blit(self.text_surface, text_rect)

        # Starting position text
        for line in text_surface.splitlines():
            line_surface = textFont.render(line, True, white)
            text_rect = line_surface.get_rect(center=(self.screen_width // x, y))
            surface.blit(line_surface, text_rect)
            y += textFont.get_linesize()# Move down by the font's line height

        # Debug: Draw debug rectangles to verify button placement
        if self.manager.debug:
            self.back_button.draw_debug(surface)
            self.forward_button.draw_debug(surface)

            # Update the display
        pygame.display.flip()

    def on_exit(self):
        super().on_exit()
