from decorators.openai_decorators import openai_function
from broadcast.broadcaster import broadcaster


@openai_function
def move_forward(speed):
    """
    {
        "description": "Moves the robot forward at a given speed.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "speed": {
                    "type": "number",
                    "description": "The speed to move forward at, an integer between 10 and 100."
                }
            },
            "required": ["speed"]
        }
    }
    """
    command = {"action": "move_forward", "speed": speed}
    broadcaster.send_message(command)

@openai_function
def move_backward(speed):
    """
    {
        "description": "Moves the robot backward at a given speed.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "speed": {
                    "type": "number",
                    "description": "The speed to move backward at, an integer between 10 and 100."
                }
            },
            "required": ["speed"]
        }
    }
    """
    command = {"action": "move_backward", "speed": speed}
    broadcaster.send_message(command)

@openai_function
def turn_left(speed, angle):
    """
    {
        "description": "Turns the robot left at a given speed and angle.",
        "is_conversational": true,
        "parameters": {
            "type": "object",
            "properties": {
                "speed": {
                    "type": "number",
                    "description": "The speed to move while turning, an integer between 10 and 100."
                },
                "angle": {
                    "type": "number",
                    "description": "The angle to turn, an integer between 0 and 180."
                }
            },
            "required": ["speed", "angle"]
        }
    }
    """
    command = {"action": "turn_left", "speed": speed, "angle": angle}
    broadcaster.send_message(command)
    return "The robot has turned left"

@openai_function
def turn_right(speed, angle):
    """
    {
        "description": "Turns the robot right at a given speed and angle.",
        "is_conversational": false,
        "parameters": {
            "type": "object",
            "properties": {
                "speed": {
                    "type": "number",
                    "description": "The speed to move while turning, an integer between 10 and 100."
                },
                "angle": {
                    "type": "number",
                    "description": "The angle to turn, an integer between 0 and 180."
                }
            },
            "required": ["speed", "angle"]
        }
    }
    """
    command = {"action": "turn_right", "speed": speed, "angle": angle}
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
