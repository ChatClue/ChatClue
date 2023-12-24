# README for `examples/` Directory

## Overview

The `examples/` directory provides practical, illustrative examples of how various components of the system can be used. It's important to note that the contents of this directory are not part of the main application. They serve as simple examples to showcase implementation strategies and to facilitate understanding of the application's capabilities.

## Current Example

- **Picar-X Example (`examples/picarx/`)**: This example demonstrates a use case involving a robot (specifically, a Picar-X) and showcases how it can be controlled with natural language through the Osiris Application. It includes a client script (`client.py`) and a movement class (`movement.py`) that utilizes the `picarx` package to execute movement commands based on specific instructions.

### Key Components

1. **Client Script (`client.py`)**: This script is designed to connect to the WebSocket server created by the main application's broadcaster, listen for incoming commands, and execute movements on the Picar-X robot accordingly. It's an end-to-end example showing how external commands can be received and translated into physical actions.

2. **Movement Class (`movement/movement.py`)**: This class encapsulates the logic for controlling the movements of the Picar-X. It translates command types into actual movement actions, such as moving forward, backward, turning, and adjusting the robot's head.

3. **Tools Integration (`tools/picarx/`)**: The `tools/picarx` directory, located in the main application, contains functions decorated with `@openai_function`. These functions define actions like moving forward, turning, etc., and are used to populate the OpenAI tools array. The Picar-X example demonstrates how these tools can be utilized in a practical scenario.

4. **Running the Example**: If you have a picarx, you can run the example by running the root directory's osiris.py script  on your computer `python3 osiris.py` (or directly on the picar if you like). Then, run the `examples/picarx/client.py` script on the picarx. Now you can chat with the application in natural language and watch the PicarX complete the requested actions.

## Purpose of this Directory

- **Educational**: These examples are great for understanding how different parts of the system work together. They can be particularly helpful for new users or developers looking to integrate similar functionalities in their projects.

## Usage

Feel free to explore these examples to better understand the application's capabilities. You can also modify them or create new ones to test different scenarios or functionalities.

Please feel free to create a branch and add additional examples here if you like. 

---

**Note**: While the examples are designed to be self-contained and functional, they may require specific hardware (like the Picar-X robot) or environmental setup to work as intended.