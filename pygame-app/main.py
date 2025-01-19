import pygame
import sys
from screens.home_screen import HomeScreen
from screens.explanation_screen import ExplanationScreen
from screens.game_screen import GameScreen
from screens.end_of_game_screen import EndOfGameScreen
from screens.feedback_screen import FeedbackScreen
from screens.repeat_screen import RepeatScreen

import asyncio
import websockets
import pygame
import json
import threading

# Dictionary to store connected clients
connected_clients = {}


# WebSocket server logic
async def handle_client(websocket):
    client_id = await websocket.recv()  # First message is the identifier
    connected_clients[client_id] = websocket
    print(f"Client connected: {client_id}")
    try:
        async for message in websocket:
            print(f"Message from {client_id}: {message}")
    except websockets.ConnectionClosed:
        print(f"Client disconnected: {client_id}")
    finally:
        connected_clients.pop(client_id, None)


# WebSocket server setup
async def websocket_server():
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("WebSocket server running on ws://0.0.0.0:8765")
    await server.wait_closed()


# Function to send a message to a specific client
async def send_message(client_id, message):
    if client_id in connected_clients:
        websocket = connected_clients[client_id]
        try:
            await websocket.send(json.dumps(message))
            print(f"Sent to {client_id}: {message}")
        except websockets.ConnectionClosed:
            print(f"Failed to send to {client_id}: Connection closed")
    else:
        print(f"Client {client_id} not found")


# Thread wrapper for running the WebSocket server
def start_websocket_server():
    asyncio.run(websocket_server())


# Screen names as constants
HOME_SCREEN = "HOME_SCREEN"
EXPLANATION_SCREEN = "EXPLANATION_SCREEN"
GAME_SCREEN = "GAME_SCREEN"
END_OF_GAME_SCREEN = "END_OF_GAME_SCREEN"
FEEDBACK_SCREEN = "FEEDBACK_SCREEN"
REPEAT_SCREEN = "REPEAT_SCREEN"


class GameManager:
    def __init__(self):

        self.debug = False

        pygame.init()
        self.screen_width = (
            1792  # >> images imported from canva: scaling of 0.93333333333
        )
        self.screen_height = 1008

        self.minimum_letter_size = 50
        self.big_letter_size = 100

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Blackboard Game")

        # Store data needed across screens
        self.shared_data = {
            "dots_pressed": 0,
            "start_time": None,
            "press_times": [],  # will store (time_stamp, circle_id)
            "end_reason": None,  # "20_reached", "timeout", or "early_abort"
            "duration": None,  # duration of last game
            "feedback": None,
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
                    self.screens[self.current_screen_name].on_exit()
                    pygame.quit()
                    sys.exit()
                ##################
                # Send command when a key is pressed
                # Example: Send a message to a client when a key is pressed
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    message = {"command": "turn_on", "led_id": 1}
                    asyncio.run(send_message("BoardESP", message))
                ##################
                # Pass events to the current screen
                self.screens[self.current_screen_name].handle_event(event)

            # Update current screen
            self.screens[self.current_screen_name].update()

            # Draw current screen
            self.screens[self.current_screen_name].draw(self.screen)

            # Flip the display
            pygame.display.flip()

            # Limit the frame rate to ~60 FPS
            self.clock.tick(60)

    def switch_screen(self, screen_name):
        """Switch to a different screen."""
        self.current_screen_name = screen_name
        self.screens[self.current_screen_name].on_enter()


def main():
    # Start WebSocket server in a separate thread
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()

    # Run the Pygame application
    game_manager = GameManager()
    game_manager.run()


if __name__ == "__main__":
    main()
