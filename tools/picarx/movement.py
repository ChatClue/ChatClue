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
def tilt_head_up(angle_increment):
    """
    {
        "description": "Tilts the robot's head up by a specified angle increment.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "angle_increment": {
                    "type": "number",
                    "description": "The angle increment to tilt the head up, an integer between 1 and 35."
                }
            },
            "required": ["angle_increment"]
        }
    }
    """
    command = {"action": "tilt_head_up", "angle_increment": angle_increment}
    broadcaster.send_message(command)

@openai_function
def tilt_head_down(angle_increment):
    """
    {
        "description": "Tilts the robot's head down by a specified angle increment.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "angle_increment": {
                    "type": "number",
                    "description": "The angle increment to tilt the head down, an integer between 1 and 35."
                }
            },
            "required": ["angle_increment"]
        }
    }
    """
    command = {"action": "tilt_head_down", "angle_increment": angle_increment}
    broadcaster.send_message(command)

@openai_function
def turn_head_left(angle_increment):
    """
    {
        "description": "Turns the robot's head to the left by a specified angle increment.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "angle_increment": {
                    "type": "number",
                    "description": "The angle increment to turn the head left, an integer between 1 and 35."
                }
            },
            "required": ["angle_increment"]
        }
    }
    """
    command = {"action": "turn_head_left", "angle_increment": angle_increment}
    broadcaster.send_message(command)

@openai_function
def turn_head_right(angle_increment):
    """
    {
        "description": "Turns the robot's head to the right by a specified angle increment.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "angle_increment": {
                    "type": "number",
                    "description": "The angle increment to turn the head right, an integer between 1 and 35."
                }
            },
            "required": ["angle_increment"]
        }
    }
    """
    command = {"action": "turn_head_right", "angle_increment": angle_increment}
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
