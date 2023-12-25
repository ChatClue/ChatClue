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
            angle_increment = command.get("angle_increment", 0)

            if action in ["move_forward", "move_backward"]:
                direction = "forward" if action == "move_forward" else "backward"
                car.move(direction, speed, angle, time)
            elif action == "tilt_head_up":
                car.tilt_head_up(angle_increment)
            elif action == "tilt_head_down":
                car.tilt_head_down(angle_increment)
            elif action == "turn_head_left":
                car.turn_head_left(angle_increment)
            elif action == "turn_head_right":
                car.turn_head_right(angle_increment)
            elif action == "stop":
                car.stop()
        else: 
            print("Not a JSON command")
    except json.JSONDecodeError:
        print("Not a JSON command")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen())
