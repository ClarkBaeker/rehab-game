import asyncio
import websockets
import pygame

esp_ip = "192.168.2.106"


async def websocket_client():
    uri = "ws://" + esp_ip + ":81"
    async with websockets.connect(uri) as websocket:
        await websocket.send("start_game")
        print("Game start command sent!")
        response = await websocket.recv()
        print(f"Received: {response}")


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pygame WebSocket Example")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Send command when a key is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            asyncio.run(websocket_client())

    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
