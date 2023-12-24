# Project Osiris

**ChatClue's Project Osiris** The objective of Project Osiris *(an Optimized System for Integrated Real-Time Interaction and Sensing)* is to create an interactive platform where users can speak naturally to their computers, robots, and IoT devices in real-time.

Originally the project was started to allow a human to communicate directly with a robot, in a natural, human-like way, and for the Robot to understand the human's instructions and to carry them out in the real world.

But, the architecture is generalizable and not limited to human and robot communication. It can also be used for human and computer communication, human and IoT device communication, or even human to computer, robot, and IoT device swarm communication.

## Getting Started

1. **Installation**: Run the `install_dependencies.sh` script to install all necessary dependencies (Tested on Ubuntu 22 and primarily designed for debian systems currently).

2. **Configuration**: Set up your `config.py` file with necessary API keys and parameters. Optionally, use environment variables for sensitive information like `GOOGLE_APPLICATION_CREDENTIALS` and `OPENAI_API_KEY`.

3. **Running the Application**: Simply execute `python3 osiris.py` after configuration. The system will be ready to start conversations using defined wake words (`config.py`) and will respond naturally using the chosen TTS (Text-to-Speech) adapter.

4. **Example Client Application**: `osiris.py` can be run on its own, but you can also listen to its broadcaster for conversation parts and structured commands to facilitate robotic and other peripheral IoT controls. An example of this type of implementation can be found in the `examples/` directory.  The current example shows how to control a robotic car with natural language by running Project Osiris and listening to it with the `examples/picarx/client.py` script running on the robotic car. The corresponding functions to control the robotic car in Project Osiris can be found in the `tools/picarx` directory, which are decorated with the project's @openai_function decorator described below.

## Key Features

### 1. **Natural two-way voice communication system**
   - Allows the user to start conversations with their predefined wake words (configured in `config.py`).
   - Handles the natural continuation of the conversation, back-and-forth, without the need to invoke the wake word again.
   - Automatically handles user interruptions of the robot / computer's response.

### 1. **Dynamic Conversation Memory and Processing**
   - Utilizes a database to store and recall all conversation data.
   - Builds conversation arrays for OpenAI based on historical data.
   - Incorporates vector embeddings for each conversation part for advanced querying and topic-based conversation structuring (i.e. Do you remember when we discussed XYZ? What did we decide was the best course of action again?). This functionality is in current development.

### 2. **Decorated Functions for Enhanced Interactivity with OpenAI Tools**
   - Creates and leverages the `@openai_function` decorator to integrate additional functionalities into OpenAI's tools array.
   - Handles tool calls and responses automatically, based on the `is_conversational` flag.
   - Example implementations and syntax can be found in the `tools/` directory.

### 3. **Broadcaster System for Device Control**
   - Features a WebSocket-based broadcaster for sending commands to clients.
   - Adaptable for various protocols (e.g., MQTT) by adding custom adapters in `broadcast/adapters`.
   - Example usage for robot control demonstrated in the `examples/` directory.

### 4. **Text-to-Speech (TTS) Capabilities**
   - Offers TTS functionality using adaptable architecture.
   - Includes offline `pyttsx3` adapter and Google Cloud's TTS API (`GTTSAdapter`).
   - Configurable via `TTS_CONFIG`, `GOOGLE_TTS_CONFIG`, and `PYTTSX3_TTS_CONFIG`.

### 5. **Optimized Conversational Flow**
   - Utilizes OpenAI's Streaming capability for quick and responsive interactions.
   - Seamless audio streaming via TTS adapter aligned with OpenAI's streaming responses.

### 6. **Background Processing with Celery and Redis**
   - Employs Celery as a background processor with Redis as the broker.
   - Enhances performance by managing tasks like conversation storage in the background.

### 7. **Ease of Installation and Configuration**
   - Includes a `install_dependencies.sh` script for setting up necessary dependencies (you'll probably still need to do a bit of tweaking. This was tested on Ubuntu 22 for reference)
   - Simple configuration through the `config.py` file and environment variables.

## Future Development

- Real-time visual processing and visual cue recognition are in the pipeline, aiming to enrich the system's interactive capabilities and broaden the scope of peripheral (robotic) control.

**Note**: This project is in active development. Stay tuned for updates and new capabilities!

---

For more detailed information about tools and examples, please refer to the individual README files in the respective directories.