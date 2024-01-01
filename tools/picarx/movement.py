from decorators.openai_decorators import openai_function
from broadcast.broadcaster import broadcaster


@openai_function
def move_forward_or_backward_right_or_left(direction, speed, angle, time):
    """
    {
        "description": "Moves the robot in a specified direction at a given speed and angle. The user can say things like move forward, make a left, turn right, etc.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["forward", "backward"],
                    "description": "The direction to move in, either 'forward' or 'backward'."
                },
                "speed": {
                    "type": "number",
                    "description": "The speed to move at, an integer between 10 and 100."
                },
                "angle": {
                    "type": "number",
                    "description": "Provide a number between -40 and 40. If you want to turn left, use a negative number. If you want to turn right, use a positive number."
                },
                "time": {
                    "type": "number",
                    "description": "The time in milliseconds to move for, an integer between 1 and 5000."
                }
            },
            "required": ["direction", "speed", "angle", "time"]
        }
    }
    """
    action = "move_forward" if direction == "forward" else "move_backward"
    command = {"action": action, "speed": speed, "angle": angle, "time": time}
    broadcaster.send_message(command)

@openai_function
def move_robot_head_up_down_left_or_right(tilt_increment, pan_increment):
    """
    {
        "description": "Moves the robot's head by tilting it up or down and by turning it left or right based on the angle increments provided. To look straight ahead, use 0 for both angles.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "tilt_increment": {
                    "type": "number",
                    "description": "The angle increment to tilt the head up or down, an integer between -40 and 40."
                },
                "pan_increment": {
                    "type": "number",
                    "description": "The angle increment to turn the head left or right, an integer between -40 and 40."
                }
            },
            "required": ["tilt_increment", "pan_increment"]
        }
    }
    """
    command = {
        "action": "move_head", 
        "tilt_increment": tilt_increment, 
        "pan_increment": pan_increment
    }
    broadcaster.send_message(command)

@openai_function
def keep_robots_focus_on_the_human():
    """
    {
        "description": "Keeps the robot's head focused on the human (the robot is track the human's movement). This should only be called if the request is to follow or track the human in some way, like 'keep your eyes on me' or 'can you keep your focus on me' or anything similar. This tool should not be called if the user is making a one time request for the robot to look somewhere specific.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
    """
    command = {
        "action": "focus_on_human"
    }
    broadcaster.send_message(command)

@openai_function
def stop(self):
    """
    {
        "description": "Stops all movement of the robot.",
        "is_conversational": false,
        "parameters": {}
    }
    """
    command = {"action": "stop"}
    broadcaster.send_message(command)
