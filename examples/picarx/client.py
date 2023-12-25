import asyncio
import websockets
import json
from vilib import Vilib
from movement.movement import PiCarXMovements

async def listen():
    uri = "ws://192.168.86.38:8765/websocket"
    car = PiCarXMovements()

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to WebSocket server at {uri}")
                while True:
                    message = await websocket.recv()
                    print(f"Message received: {message}")
                    process_command(car, message)
        except websockets.ConnectionClosed:
            print("WebSocket connection closed. Reconnecting...")
            await asyncio.sleep(5)  # Wait 5 seconds before trying to reconnect
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)  # Wait 5 seconds before trying to reconnect

def process_command(car, message):
    try:
        command = json.loads(message)
        if isinstance(command, dict):
            action = command.get("action")
            time_val = command.get("time", 1) / 1000  # Convert milliseconds to seconds
            speed = command.get("speed", 0)
            angle = command.get("angle", 0)
            tilt_increment = command.get("tilt_increment", 0)
            pan_increment = command.get("pan_increment", 0)

            if action in ["move_forward", "move_backward"]:
                direction = "forward" if action == "move_forward" else "backward"
                car.move(direction, speed, angle, time_val)
            elif action == "move_head":
                car.move_head(tilt_increment, pan_increment)
            elif action == "stop":
                car.stop()
        else: 
            print("Not a JSON command")
    except json.JSONDecodeError:
        print("Not a JSON command")

if __name__ == "__main__":
    try:
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=True,web=True)
        asyncio.get_event_loop().run_until_complete(listen())
    finally:
        Vilib.camera_close()
