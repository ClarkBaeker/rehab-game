import pygame
import pygame_gui
from games.connect_dots import TouchDots
from screens.screen_interface import ScreenInterface
from utils.utils import render_text
from utils.invisible_button import InvisibleButton


game_mode_mapping = {
    "Connect the Dots": TouchDots,
    "Circle the Dots": TouchDots,
}


class GameSelectionScreen(ScreenInterface):
    def __init__(self, manager):
        super().__init__(manager)

        # Load the background with arrows
        self.background = pygame.image.load("images/game.png").convert()

        # UI manager for managing GUI elements
        self.ui_manager = pygame_gui.UIManager(
            (manager.screen_width, manager.screen_height),
            theme_path="styles/game_select_dropdown.json",
        )

        # Dropdown to select game mode
        self.game_mode_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["Connect the Dots", "Circle the Dots"],
            starting_option="Connect the Dots",  # default
            relative_rect=pygame.Rect(
                manager.screen_width // 2 - 125,
                manager.screen_height // 2,
                250,
                80,
            ),
            manager=self.ui_manager,
        )

        self.level_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["Level 1", "Level 2", "Level 3"],
            starting_option="Level 1",  # default
            relative_rect=pygame.Rect(
                manager.screen_width // 2 - 125,
                manager.screen_height // 2 + 80,
                250,
                80,
            ),
            manager=self.ui_manager,
        )

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
        self.manager.shared_data["game_mode"] = self.game_mode_dropdown.selected_option[
            0
        ]
        selected_game_class = game_mode_mapping.get(
            self.game_mode_dropdown.selected_option[0], TouchDots
        )
        self.manager.shared_data["level"] = self.level_dropdown.selected_option[0]
        print(
            f"{self.manager.shared_data['game_mode']} ({self.manager.shared_data['level']}) has been selected."
        )
        self.manager.game = selected_game_class(self.manager)
        self.manager.switch_screen("EXPLANATION_SCREEN")

    def handle_event(self, event):
        # Let the UI manager handle GUI events
        self.ui_manager.process_events(event)
        # Delegate events to the invisible buttons
        self.back_button.handle_event(event)
        self.forward_button.handle_event(event)

    def update(self):
        super().update()
        time_delta = self.manager.clock.get_time() / 1000.0
        self.ui_manager.update(time_delta)

    def draw(self, surface):
        super().draw(surface)

        # Draw the background
        surface.blit(self.background, (0, 0))

        # Font
        titleFont = pygame.font.Font(None, 150)
        textFont = pygame.font.Font(None, 60)
        white = (255, 255, 255)

        # text and title
        title_surface = titleFont.render(
            "Spielauswahl", True, white
        )  # True enables anti-aliasing
        text_surface = """
        Bitte wählen Sie ein Spiel und ein Level aus."""

        # Get the rectangles for positioning
        x, y = 180, 200

        # title
        title_rect = title_surface.get_rect(topleft=(300, 100))  # Centered at the top
        surface.blit(title_surface, title_rect)

        # Starting position text
        for line in text_surface.splitlines():
            line_surface = textFont.render(line, True, white)
            text_rect = line_surface.get_rect(topleft=(x, y))
            surface.blit(line_surface, text_rect)
            y += textFont.get_linesize() + 10  # Move down by the font's line height

        self.ui_manager.draw_ui(surface)

        # Update the display
        pygame.display.flip()

    def on_exit(self):
        super().on_exit()
