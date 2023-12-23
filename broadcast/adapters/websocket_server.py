import asyncio
import websockets
import threading
import queue
import json
import time
from config import BROADCAST_WEBSOCKET_CONFIG

class WebSocketServer:
    """
    A WebSocket server class for handling real-time messaging.

    This class sets up a WebSocket server, manages client connections, and handles message broadcasting.

    Attributes:
        host (str): The host address for the WebSocket server.
        port (int): The port number for the WebSocket server.
        connected_clients (set): A set of connected WebSocket clients.
        message_queue (queue.Queue): A queue for storing messages to be broadcasted.
        loop (asyncio.new_event_loop): An asyncio event loop for asynchronous operations.
    """

    def __init__(self):
        """
        Initializes the WebSocket server with host and port settings from the configuration.
        """
        self.host = BROADCAST_WEBSOCKET_CONFIG.get("websocket_host", "localhost")
        self.port = BROADCAST_WEBSOCKET_CONFIG.get("websocket_port", 8765)
        self.server_thread = None
        self.connected_clients = set()
        self.message_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()
        self.shutdown_event = asyncio.Event()

    async def echo(self, websocket, path):
        """
        An asynchronous method to echo messages received from clients.

        Args:
            websocket: The WebSocket connection instance.
            path (str): The HTTP path for the WebSocket connection.
        """
        self.connected_clients.add(websocket)
        try:
            async for message in websocket:
                print(f"Received message: {message}")
                if self.shutdown_event.is_set():
                    break  # Exit if shutdown event is set
                await websocket.send(f"Echo: {message}")
        finally:
            self.connected_clients.remove(websocket)

    async def send_message_to_clients(self):
        """
        An asynchronous method to send messages from the queue to all connected clients.
        """
        while not self.shutdown_event.is_set():
            message = await asyncio.to_thread(self.message_queue.get)
            if self.connected_clients:
                await asyncio.wait([client.send(message) for client in self.connected_clients])

    def send_message(self, message):
        """
        Puts a message in the queue to be broadcasted to clients.

        Args:
            message: The message to be sent.
        """
        try:
            # Try to serialize the message as JSON
            serialized_message = json.dumps(message)
        except TypeError:
            # If not JSON, just send along the string representation
            serialized_message = str(message)
        self.message_queue.put(serialized_message)

    async def start_server(self):
        """
        Starts the server and runs the asyncio event loop.
        """
        await asyncio.gather(
            websockets.serve(self.echo, self.host, self.port),
            self.send_message_to_clients()
        )

    def start(self):
        """
        Sets up the WebSocket server and starts listening for connections.
        """
        start_server = websockets.serve(self.echo, self.host, self.port)
        asyncio.get_event_loop().create_task(self.send_message_to_clients())
        return start_server
    
    async def server_loop(self):
        """
        A loop that continues until the shutdown event is set.
        """
        while not self.shutdown_event.is_set():
            await asyncio.sleep(0.1)
    
    async def stop_loop(self):
        """
        An asynchronous method to stop the event loop after a short delay.
        """
        # Cancel all remaining asyncio tasks
        tasks = [t for t in asyncio.all_tasks(self.loop) if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Close all clients
        for client in self.connected_clients:
            await client.close()

        # Stop the loop
        self.loop.stop()
    
    def schedule_shutdown(self):
        """
        Schedules the shutdown of the server, closing all client connections and stopping the event loop.
        """
        asyncio.run_coroutine_threadsafe(self.stop_loop(), self.loop)

    def run(self):
        """
        Runs the WebSocket server on a separate daemon thread.
        """
        self.server_thread = threading.Thread(target=self.loop.run_until_complete, args=(self.start_server(),), daemon=True)
        self.server_thread.start()
        
    def shutdown(self):
        """
        Initiates the shutdown process for the WebSocket server.
        """
        if self.server_thread:
            self.shutdown_event.set()
            self.schedule_shutdown()
            # Adding an additional loop stop command for safety
            self.loop.call_soon_threadsafe(self.loop.stop)
            while self.loop.is_running():
                time.sleep(0.1)
            self.loop.close()
            print("IS RUNNING", self.loop.is_running())
            print("THREAD IS RUNNING", self.server_thread.is_alive())
            print("TREAD IS DAEMON", self.server_thread.daemon)
