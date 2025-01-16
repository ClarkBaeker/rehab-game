import pygame
import sys
from screens.home_screen import HomeScreen
from screens.explanation_screen import ExplanationScreen
from screens.game_screen import GameScreen
from screens.end_of_game_screen import EndOfGameScreen
from screens.feeeback_screen import FeedbackScreen
from screens.repeat_screen import RepeatScreen

import asyncio
import websockets
import pygame
import json

esp_ip = "192.168.2.106"

message = {"command": "turn_on", "led_id": 1}

async def websocket_client():
    uri = "ws://" + esp_ip + ":81"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(message))
        print("Game start command sent!")
        """ response = await websocket.recv()
        print(f"Received: {response}") """


# Screen names as constants 
HOME_SCREEN = "HOME_SCREEN"
EXPLANATION_SCREEN = "EXPLANATION_SCREEN"
GAME_SCREEN = "GAME_SCREEN"
END_OF_GAME_SCREEN = "END_OF_GAME_SCREEN"
FEEDBACK_SCREEN = "FEEDBACK_SCREEN"
REPEAT_SCREEN = "REPEAT_SCREEN"

class GameManager:
    def __init__(self):
        
        self.debug = True 
        
        pygame.init()
        self.screen_width = 1792 # >> images imported from canva: scaling of 0.93333333333
        self.screen_height = 1008

        self.minimum_letter_size = 50
        self.big_letter_size = 100
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Blackboard Game")

        # Store data needed across screens
        self.shared_data = {
            "dots_pressed": 0,
            "start_time": None,
            "press_times": [],   # will store (time_stamp, circle_id)
            "end_reason": None,  # "20_reached", "timeout", or "early_abort"
            "duration": None,   # duration of last game
            "feedback": None
        }

        # The clock is used to limit FPS and track time
        self.clock = pygame.time.Clock()
        self.current_screen_name = HOME_SCREEN
        
        # Create instances of all screens
        self.screens = {
            HOME_SCREEN: HomeScreen(self),
            EXPLANATION_SCREEN: ExplanationScreen(self),
            GAME_SCREEN: GameScreen(self),
            END_OF_GAME_SCREEN: EndOfGameScreen(self),
            FEEDBACK_SCREEN: FeedbackScreen(self),
            REPEAT_SCREEN: RepeatScreen(self), 
        }

    def run(self):
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Pass events to the current screen
                self.screens[self.current_screen_name].handle_event(event)

            # Update current screen
            self.screens[self.current_screen_name].update()

            # Draw current screen
            self.screens[self.current_screen_name].draw(self.screen)

            ##################
            # Send command when a key is pressed
            # if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # asyncio.run(websocket_client())
            ##################
            
            # Flip the display
            pygame.display.flip()

            # Limit the frame rate to ~60 FPS
            self.clock.tick(60)

    def switch_screen(self, screen_name):
        """ Switch to a different screen. """
        self.current_screen_name = screen_name

def main():
    game_manager = GameManager()
    game_manager.run()

if __name__ == "__main__":
    main()
