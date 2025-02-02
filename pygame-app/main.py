import pygame
import sys
import os
from pathlib import Path

from games.connect_dots import TouchDots
from games.game_interface import GameInterface
from screens.home_screen import HomeScreen
from screens.explanation_screen import ExplanationScreen
from screens.game_screen import GameScreen
from screens.end_of_game_screen import EndOfGameScreen
from screens.feedback_screen import FeedbackScreen
from screens.repeat_screen import RepeatScreen
from screens.configuration_screen import ConfigurationScreen
from screens.explanation_screen_connectDots import ExplanationConnectDots
from screens.explanation_screen_circleDots import ExplanationCircleDots

import asyncio
import websockets
import pygame
import json
import threading

from utils.logger import Logger

# Dictionary to store connected clients
connected_clients = {}


def handle_message(client_id, message, game_manager):
    print(f"Message from {client_id}: {message}")
    message_json = json.loads(message)
    # Example: Handle message from KneeESP
    if client_id == "KneeESP":
        if message_json["field"] == "angle":
            game_manager.logger.append_knee_angle(message_json["value"])


# WebSocket server logic
async def handle_client(websocket, game_manager):
    client_id = await websocket.recv()  # First message is the identifier
    connected_clients[client_id] = websocket
    print(f"Client connected: {client_id}")
    try:
        async for message in websocket:
            handle_message(client_id, message, game_manager)
    except websockets.ConnectionClosed:
        print(f"Client disconnected: {client_id}")
    finally:
        connected_clients.pop(client_id, None)


# WebSocket server setup
async def websocket_server(game_manager):
    server = await websockets.serve(
        lambda ws: handle_client(ws, game_manager), "0.0.0.0", 8765
    )
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
def start_websocket_server(game_manager):
    asyncio.run(websocket_server(game_manager))


# Screen names as constants
HOME_SCREEN = "HOME_SCREEN"
EXPLANATION_SCREEN = "EXPLANATION_SCREEN"
GAME_SCREEN = "GAME_SCREEN"
END_OF_GAME_SCREEN = "END_OF_GAME_SCREEN"
FEEDBACK_SCREEN = "FEEDBACK_SCREEN"
REPEAT_SCREEN = "REPEAT_SCREEN"
CONFIGURATION_SCREEN = "CONFIGURATION_SCREEN"
EXPLANATION_SCREEN_CONNECTDOTS = "EXPLANATION_SCREEN_CONNECTDOTS"
EXPLANATION_SCREEN_CIRCLEDOTS = "EXPLANATION_SCREEN_CIRCLEDOTS"

# ESP clients
BOARD_CLIENT = "BoardESP"
KNEE_CLIENT = "KneeESP"


class GameManager:
    def __init__(self):

        self.debug = False  # TODO

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
            "game_mode": "Connect the Dots",
            "level": "Level 1",
            "input_mode": "mouse",  # setting the default
            "start_time": None,
            "end_reason": None,  # "win", "timeout", or "early_abort"
            "duration": None,  # duration of game
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
            CONFIGURATION_SCREEN: ConfigurationScreen(self),
            EXPLANATION_SCREEN_CONNECTDOTS: ExplanationConnectDots(self),
            EXPLANATION_SCREEN_CIRCLEDOTS: ExplanationCircleDots(self),
        }

        # Initialize logger
        self.logger = Logger()

        self.clients = [BOARD_CLIENT, KNEE_CLIENT]

        # Game dependent variables
        self.game: GameInterface = TouchDots(self)

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
        self.screens[self.current_screen_name].on_exit()
        self.current_screen_name = screen_name
        self.screens[self.current_screen_name].on_enter()

    def send_message(self, client_id, message):
        if client_id not in self.clients:
            print(f"Client {client_id} not found")
            return
        asyncio.run(send_message(client_id, message))


def main():
    # Create Pygame application
    game_manager = GameManager()

    # Start WebSocket server in a separate thread
    websocket_thread = threading.Thread(
        target=start_websocket_server, args=(game_manager,), daemon=True
    )
    websocket_thread.start()

    # Run the game
    game_manager.run()


if __name__ == "__main__":
    main()
