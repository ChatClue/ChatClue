import asyncio
import websockets
import threading
import queue
import json
from config import BROADCAST_WEBSOCKET_CONFIG

class WebSocketServer:
    def __init__(self):
        self.host = BROADCAST_WEBSOCKET_CONFIG.get("websocket_host", "localhost")
        self.port = BROADCAST_WEBSOCKET_CONFIG.get("websocket_port", 8765)
        self.connected_clients = set()
        self.message_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()

    async def echo(self, websocket, path):
        self.connected_clients.add(websocket)
        try:
            async for message in websocket:
                print(f"Received message: {message}")
                await websocket.send(f"Echo: {message}")
        finally:
            self.connected_clients.remove(websocket)

    async def send_message_to_clients(self):
        while True:
            message = await asyncio.to_thread(self.message_queue.get)
            if self.connected_clients:
                await asyncio.wait([client.send(message) for client in self.connected_clients])

    def send_message(self, message):
        try:
            # Try to serialize the message as JSON
            serialized_message = json.dumps(message)
        except TypeError:
            # If not JSON, just send along the string representation
            serialized_message = str(message)

        self.message_queue.put(serialized_message)

    def start_server(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start())
        self.loop.run_forever()

    def start(self):
        start_server = websockets.serve(self.echo, self.host, self.port)
        asyncio.get_event_loop().create_task(self.send_message_to_clients())
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    
    async def stop_loop(self):
        # Wait for a short period to allow client connections to close
        await asyncio.sleep(0.1)
        self.loop.stop()
    
    def schedule_shutdown(self):
        # Schedule the closing of all client connections
        for client in self.connected_clients:
            asyncio.ensure_future(client.close(), loop=self.loop)

        # Schedule the stopping of the event loop
        asyncio.ensure_future(self.stop_loop(), loop=self.loop)


    def run(self):
        threading.Thread(target=self.start_server, daemon=True).start()

    def shutdown(self):
        self.schedule_shutdown()