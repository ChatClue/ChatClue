import asyncio
from concurrent.futures import ThreadPoolExecutor
import websockets
import json
from vilib import Vilib
from movement.movement import PiCarXMovements

async def listen(car):
    uri = "ws://192.168.86.38:8765/websocket"
    #start_following_human(car)  # Start focusing on human

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to WebSocket server at {uri}")
                while True:
                    message = await websocket.recv()
                    print(f"Message received: {message}")
                    #stop_following_human()  # Stop following human to process command
                    process_command(car, message)
                    #start_following_human()  # Resume following human
        except websockets.ConnectionClosed:
            print("WebSocket connection closed. Reconnecting...")
            await asyncio.sleep(5)  # Wait 5 seconds before trying to reconnect
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)  # Wait 5 seconds before trying to reconnect

def start_following_human(car):
    # car.start_follow_the_human()
    car.start_focus_on_human()

def stop_following_human(car):
    # car.stop_follow_the_human()
    car.stop_focus_on_human()

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

async def main(car):
    # Run Vilib.display in a separate thread
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_running_loop()
        await listen(car)
        await loop.run_in_executor(executor, lambda: Vilib.display(local=True, web=True))
        # Continue with WebSocket listening

if __name__ == "__main__":
    car = PiCarXMovements()  # Initialize car object
    listen(car)
    # try:
    #     Vilib.camera_start(vflip=False, hflip=False)
    #     asyncio.run(main(car))
    # finally:
    #     Vilib.camera_close()
    #     stop_following_human(car)
    #     car.reset()
