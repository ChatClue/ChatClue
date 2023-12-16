import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8765"  # Replace with your server's URI if different

    async with websockets.connect(uri) as websocket:
        print(f"Connected to WebSocket server at {uri}")
        while True:
            message = await websocket.recv()
            print(f"Message received: {message}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen())
