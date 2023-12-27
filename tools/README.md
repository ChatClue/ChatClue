# Tools Directory

## Overview

This directory, `tools/`, is dedicated to defining tools with metadata compatible with OpenAI's tools parameter. The purpose of these tools is to provide a structured and standardized way of defining functions that can be utilized in conjunction with OpenAI's API, particularly in chat completions.

## How It Works

Each tool is defined as a Python function and decorated with `@openai_function`. This decorator marks the function as an OpenAI tool and extracts its metadata from the docstring. The metadata includes a description of the tool, its conversational context (whether it requires further conversation or not), and its parameters.

The `openai_function` decorator processes the function and its metadata, registering it in a global `openai_functions` list. This list is then used to populate the tools parameter in chat completion requests to the OpenAI API.

### Defining New Tools

To define a new tool:
1. Create a Python function that encapsulates the desired tool functionality.
2. Annotate the function with the `@openai_function` decorator.
3. Write a JSON-formatted docstring that describes the tool, including its parameters and whether it is conversational.
4. Add the tool function to an appropriate subdirectory within `tools/` (your choice).

## Example Tool Definition

```python
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
```

## Helpful Note

In the above example, we are using the "broadcaster" to broadcast the command via a WebSocket to inform any listening robots of the request to move. In a practical application, the action does not need to be broadcasted, and instead can perform its action directly in the function and provide feedback immediately if needed.

If the function is marked as "is_conversational", then the system will autotically structure another chat completion request, with the original tool request and corresponding tool response returned by your function, and send it along to OpenAI to continue the conversation.

## Current Directory Structure

### robot

- **Purpose**: Contains tool definitions specifically designed to control a robotic entity (e.g., PiCar-X).
- **Relation to PiCar-X Client**: The functions in the `tools/robot` directory are aligned with the `examples/picarx/` client example. The client example listens to a WebSocket connection created by a broadcaster in the main application. When tool functions like are invoked, they send commands over this WebSocket, which the PiCar-X client then listens to and executes.

This is only an example. But, if you have a picarx, it should work as expected if you run the `examples/picarx/client.py` script on your programmable car's RaspberryPi. 

### video

- **Purpose**: Handles video image analysis. This is part of the main application.