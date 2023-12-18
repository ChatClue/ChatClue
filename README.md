# Project Osiris

**ChatClue's Project Osiris** is a comprehensive system designed for real-time audio and visual communication processing, integrating dynamic LLM (Large Language Models) memory and control over robotic functions and IoT devices. The primary goal of Project Osiris *(Optimized System for Integrated Real-Time Interaction and Sensing)* is to create an interactive platform where users can communicate naturally with their computers in real-time, with an advanced ability to manage and recall conversations and control external devices or functions.

## Key Features

### 1. **Dynamic Conversation Memory and Processing**
   - Utilizes a database to store and recall all conversation data.
   - Builds conversation arrays for OpenAI based on historical data.
   - Incorporates vector embeddings for each conversation part for advanced querying and topic-based conversation structuring.

### 2. **Decorated Functions for Enhanced Interactivity**
   - Leverages `@openai_function` decorator to integrate additional functionalities into OpenAI's tools array.
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
   - Utilizes OpenAI's Streaming capability for prompt and responsive interactions.
   - Seamless audio streaming via TTS adapter aligned with OpenAI's streaming responses.

### 6. **Background Processing with Celery and Redis**
   - Employs Celery as a background processor with Redis as the broker.
   - Enhances performance by managing tasks like conversation storage in the background.

### 7. **Ease of Installation and Configuration**
   - Includes a `install_dependencies.sh` script for setting up necessary dependencies (you'll probably still need to do a bit of tweaking. This was tested on Ubuntu 22 for reference)
   - Simple configuration through the `config.py` file and environment variables.

## Getting Started

1. **Installation**: Run the `install_dependencies.sh` script to install all necessary dependencies.

2. **Configuration**: Set up your `config.py` file with necessary API keys and parameters. Optionally, use environment variables for sensitive information like `GOOGLE_APPLICATION_CREDENTIALS` and `OPENAI_API_KEY`.

3. **Running the Application**: Simply execute `python3 osiris.py` after configuration. The system will be ready to start conversations using defined wake words and respond naturally using the chosen TTS adapter.

4. **Example Client Application**: Project Osiris can be run on its own, but you can also listen to its broadcaster for conversation parts and structured commands to facilitate robotic and other peripheral IoT controls. An example of this type of implementation can be found in the `examples/` directory.  The current example shows how to control a robotic car with natural language only by running Project Osiris and listening to it with the `examples/picarx/client.py` script running on the robotic car.

## Future Development

- Real-time visual processing and visual cue recognition are in the pipeline, aiming to enrich the system's interactive capabilities and broaden the scope of peripheral (robotic) control.

**Note**: This project is in active development. Stay tuned for updates and new capabilities!

---

For more detailed information about tools and examples, please refer to the individual README files in the respective directories.