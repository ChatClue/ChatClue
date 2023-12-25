import asyncio
import websockets
import json
from movement.movement import PiCarXMovements

async def listen():
    uri = "ws://192.168.86.38:8765/websocket"
    car = PiCarXMovements()

    async with websockets.connect(uri) as websocket:
        print(f"Connected to WebSocket server at {uri}")
        while True:
            message = await websocket.recv()
            print(f"Message received: {message}")
            process_command(car, message)

def process_command(car, message):
    try:
        command = json.loads(message)
        if isinstance(command, dict):
            action = command.get("action")
            time = command.get("time", 1) / 1000  # Convert milliseconds to seconds
            speed = command.get("speed", 0)
            angle = command.get("angle", 0)
            tilt_increment = command.get("tilt_increment", 0)
            pan_increment = command.get("pan_increment", 0)

            if action in ["move_forward", "move_backward"]:
                direction = "forward" if action == "move_forward" else "backward"
                car.move(direction, speed, angle, time)
            elif action == "move_head":
                tilt_increment = tilt_increment
                pan_increment = pan_increment
                car.move_head(tilt_increment, pan_increment)
            elif action == "stop":
                car.stop()
        else: 
            print("Not a JSON command")
    except json.JSONDecodeError:
        print("Not a JSON command")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen())
