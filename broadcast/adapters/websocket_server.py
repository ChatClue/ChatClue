import asyncio
import websockets
import threading
import json
from config import BROADCAST_WEBSOCKET_CONFIG

class WebSocketServer:
    def __init__(self):
        self.host = BROADCAST_WEBSOCKET_CONFIG.get("websocket_host", "localhost")
        self.port = BROADCAST_WEBSOCKET_CONFIG.get("websocket_port", 8765)
        self.connected_clients = set()
        self.loop = asyncio.new_event_loop()
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)

    async def handler(self, websocket, path):
        self.connected_clients.add(websocket)
        try:
            async for message in websocket:
                print(f"Received message: {message}")
        except websockets.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)

    def send_message(self, message):
        try:
            serialized_message = json.dumps(message)
        except: 
            serialized_message = str(message)
        asyncio.run_coroutine_threadsafe(self.broadcast(serialized_message), self.loop)

    async def broadcast(self, message):
        if self.connected_clients:
            await asyncio.wait([ws.send(message) for ws in self.connected_clients])

    def run_server(self):
        asyncio.set_event_loop(self.loop)
        start_server = websockets.serve(self.handler, self.host, self.port)
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    def run(self):
        self.server_thread.start()

    def shutdown(self):
        asyncio.run_coroutine_threadsafe(self.close_all_connections(), self.loop)
        self.loop.call_soon_threadsafe(self.loop.stop)

    async def close_all_connections(self):
        for client in self.connected_clients:
            await client.close()
        self.connected_clients.clear()
