import threading
import websocket
import json
import time
from vilib import Vilib
from movement.movement import PiCarXMovements

def listen(car):
    uri = "ws://192.168.86.38:8765/websocket"
    start_following_human(car)

    while True:
        try:
            ws = websocket.create_connection(uri)
            print(f"Connected to WebSocket server at {uri}")
            while True:
                message = ws.recv()
                print(f"Message received: {message}")
                stop_following_human(car)
                process_command(car, message)
                start_following_human(car)
        except websocket.WebSocketConnectionClosedException:
            print("WebSocket connection closed. Reconnecting...")
            time.sleep(5)
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def start_following_human(car):
    car.start_focus_on_human()

def stop_following_human(car):
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

if __name__ == "__main__":
    car = PiCarXMovements()  # Initialize car object
    try:
        # Create and start video display thread
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=True,web=True)

        # Create and start WebSocket listening thread
        listen_thread = threading.Thread(target=listen, args=(car,), daemon=True)
        listen_thread.start()

        # Keep the main thread alive while the other threads are running
        listen_thread.join()
    finally:
        stop_following_human(car)
        Vilib.camera_close()
        car.reset()