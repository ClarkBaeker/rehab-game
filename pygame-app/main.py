import asyncio
import websockets
import pygame
import threading

# Dictionary to store connected clients
connected_clients = {}


# WebSocket server logic
async def handle_client(websocket, path):
    client_id = await websocket.recv()  # First message is the identifier
    connected_clients[client_id] = websocket
    print(f"Client connected: {client_id}")
    try:
        async for message in websocket:
            print(f"Message from {client_id}: {message}")
            # Process incoming messages from ESP32 if needed
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
            await websocket.send(message)
            print(f"Sent to {client_id}: {message}")
        except websockets.ConnectionClosed:
            print(f"Failed to send to {client_id}: Connection closed")
    else:
        print(f"Client {client_id} not found")


# Thread wrapper for running the WebSocket server
def start_websocket_server():
    asyncio.run(websocket_server())


# Pygame setup
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pygame with WebSocket Server")
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Example: Send a message to a client when a key is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if "BoardESP" in connected_clients.keys():
                    asyncio.run(
                        send_message(connected_clients["BoardESP"], "Turn on LED 1")
                    )

        # Game logic and rendering
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


# Main function
if __name__ == "__main__":
    # Start WebSocket server in a separate thread
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()

    # Run the Pygame application
    run_game()
