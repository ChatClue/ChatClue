AUDIO_SETTINGS = {
    # List of phrases that, when detected, indicate a request for quiet or silence.
    # These phrases are used by the system to recognize when it should stop speaking or reduce noise.
    "QUIET_PLEASE_PHRASES": [
        "be noiseless", "button it", "calm your voice", "cease speaking", 
        "cease your chatter", "close your mouth", "cut it out", "don't speak", 
        "end the noise", "enough", "go mute", "hush", "hush down", 
        "hush now", "keep quiet", "keep it down", "keep the silence", "mums the word", 
        "mute", "muzzle it", "no chit chat", "no more words", "no talking", 
        "not another word", "please stop", "put a lid on it", "quiet", "quietude", 
        "shh", "shhh", "shut up", "silence", "silence yourself", "silence your lips", 
        "speechless", "sshh", "stay mum", "stifle your speech", "stop", "stop babbling", 
        "stop blabbering", "stop please", "stop talking", "tone it down"
    ],
    # List of wake words or phrases used to activate the robot or system.
    # These are keywords the system listens for to start processing voice commands.
    "WAKE_PHRASES": ["robot", "computer"],

    # List of phrases that will be used to let the user know that a specific tool or piece of information
    # Could not be retrieved.  This is specifically in relation to functionality associated with the 
    # OpenAI API chat completion's tools parameter and corresponding responses.  
    "TOOL_NOT_FOUND_PHRASES": [
        "I apologize, but I'm experiencing some difficulties accessing the tool or information you're looking for. Could you please try again?",
        "I'm sorry, I've encountered an issue while trying to retrieve the tool or information you asked for. Please give it another try.",
        "I regret to inform you that I'm having trouble accessing the requested tool or information. Would you mind trying once more?",
        "I'm experiencing some challenges in fetching the tool or information you need. Could you kindly attempt it again?",
        "I'm sorry, but there seems to be a problem with accessing the tool or information you need. Please try again.",
        "Unfortunately, I'm unable to access the tool or information you requested at the moment. Please try again shortly.",
        "I apologize for the inconvenience, but I'm currently having trouble accessing the requested tool or information. Please try again later.",
        "I'm facing some issues in obtaining the tool or information you requested. Would you please try again?",
        "I'm sorry to report that I'm unable to retrieve the tool or information you're seeking right now. Please try again.",
        "I regret that I'm encountering difficulties with accessing the tool or information you need. Could you please try again later?"
    ],

    # The sample rate for audio input. This is the number of samples of audio carried per second.
    # Higher sample rates can provide better quality but require more processing power.
    "SOUND_DEVICE_SAMPLERATE": 48000,

    # Filename for dumping audio input. Useful for debugging or processing audio data offline.
    "AUDIO_IN_DUMP_FILENAME": "output.wav",

    # The language model used for speech recognition (e.g., English US).
    "VOSK_MODEL": "en-us",

    # The block size for audio processing. Determines how much audio data is processed at once.
    "SOUND_DEVICE_BLOCK_SIZE": 28000,

    # The name of the sound input device to be used. 'default' uses the system's default device.
    "SOUND_DEVICE_DEVICE": "default"
}

OPENAI_SETTINGS = {
    # OpenAI API key for accessing GPT models. Uncomment and set your key here if not using an environment variable.
    #"api_key": "sk-<your-openai-api-key>",

    # The specific model of GPT to use for generating responses (e.g., 'gpt-3.5-turbo').
    "model": "gpt-4-1106-preview",

    # Model used for embedding text into a numerical format, useful in certain applications like semantic search.
    "embedding_model": "text-embedding-ada-002",

    # Maximum number of tokens (words) that can be used in the context for the GPT model.
    "max_context_tokens": 2500,

    # Initial message or instruction to the GPT model, setting the tone and context for the interaction.
    "initial_system_message": "You are a physical robot with the ability to take physical actions in the world based on user requests. You are also an assistant and conversational."
}

DATABASE_CONFIG = {
    # Name of the database to be used for storing conversations and other data.
    'dbname': 'conversations',

    # Username for the database. Typically 'postgres' for PostgreSQL databases.
    'user': 'postgres',

    # Password for the database user. Keep this secure.
    'password': '',

    # Host address for the database. 'localhost' refers to the local machine.
    'host': 'localhost',

    # Port number for connecting to the database.
    'port': '5432'
}


CONVERSATIONS_CONFIG = {
    # Identifier for user in the conversation database.
    "user": 1,

    # Identifier for the assistant (robot or AI) in the conversation database.
    "assistant": 2
}

CELERY_CONFIG = {
    # Determines whether to run Celery locally and automatically. 
    # Set to False for manual start or in production environments. True is preferable for development.
    # Manual starts can be achieved by running the following command in the terminal:
    # - celery -A osiris.celery_app worker --loglevel=info
    "RUN_LOCALLY_AUTOMATICALLY": True,

    # Logging level for Celery. Use "debug" for more verbose output, helpful in development.
    "LOCAL_LOG_LEVEL": "info",

    # The name of the application using Celery.
    "APPLICATION_NAME": "osiris",

    # URL for the Celery broker, specifying the transport and location. Here, Redis is used as the broker.
    "BROKER_URL": 'redis://localhost:6379/0'
}


TTS_CONFIG = {
    # Specifies the adapter class to be used for text-to-speech (TTS) functionality.
    # The value should be a string representing the module and class name of the TTS adapter.
    # Example: "audio.adapters.gtts.GTTSAdapter" for using Google Text-to-Speech.
    #
    # Currently available adapters (defined in audio/tts_adapters)):
    #  - audio.tts_adapters.gtts.GTTSAdapter
    #  - audio.tts_adapters.pyttsx3.Pyttsx3Adapter
    #
    # Note: The Pyttsx3Adapter processes requests offline and does not require an API key.
    #
    # Additional Adapters: Please feel free to add your own adapter classes to the audio/tts_adapters 
    #                      directory for your own TTS service / models. 

    "tts_adapter": "audio.tts_adapters.gtts.GTTSAdapter",
    # "tts_adapter": "audio.tts_adapters.pyttsx3.Pyttsx3Adapter",
}

# Optional audio.tts_adapters.gtts.GTTSAdapter configuration.
GOOGLE_TTS_CONFIG = {
    # Optional. Path to the JSON file containing your Google Cloud API key.
    # Uncomment and provide the path if you are not using the GOOGLE_APPLICATION_CREDENTIALS environment variable.
    #'api_key_path': 'path/to/api_key.json',

    # Optional. Specifies the voice model to be used for speech synthesis.
    # Example: 'en-US-Wavenet-D' for a specific English (US) voice model.
    'voice_model': 'en-US-Wavenet-D',

    # Optional. Language code for the TTS engine.
    # Example: 'en-US' for American English. This should match with the selected voice model.
    'language_code': 'en-US',

    # Optional. Default speaking rate for the synthesized speech.
    # 1.0 represents a normal speaking rate. Range: 0.25 (slow) to 4.0 (fast).
    # The robot may adjust this dynamically depending on the context of the conversation.
    'speaking_rate': 1.0,

    # Optional. Pitch adjustment for the synthesized speech.
    # Range: -20.0 (lower pitch) to 20.0 (higher pitch). 0 is the default pitch.
    # The robot can modify this value dynamically if needed.
    'pitch': 0,

    # Optional. Volume gain for the synthesized speech in decibels (dB).
    # Range: -96.0 (quieter) to 16.0 (louder), with 0 being the default level.
    # The robot can modify this value dynamically based on the environment or context.
    'volume_gain_db': 0,

    # Optional. Specifies the audio encoding of the output file.
    # Options include 'LINEAR16' (uncompressed PCM audio), 'MP3', and 'OGG_OPUS'.
    # The choice of encoding affects the quality and size of the output audio file.
    'audio_encoding': 'LINEAR16',
}

# Optional audio.tts_adapters.pyttsx3.Pyttsx3Adapter configuration.
# Learn more about Pyttsx3 configuration options: https://github.com/nateshmbhat/pyttsx3
PYTTSX3_TTS_CONFIG = {
    # "rate": Controls the speaking rate of the synthesized speech.
    # The value is in words per minute. Default is typically around 200 wpm.
    "rate": 175,

    # "volume": Sets the volume for the synthesized speech.
    # The value ranges from 0.0 (silent) to 1.0 (maximum volume).
    # Example: 1.0 for maximum volume.
    "volume": 1.0,

    # "voice": Specifies the voice ID to be used for speech synthesis.
    # The available voices can depend on the system and pyttsx3 installation.
    # Example: 'voices[0].id' for a default male voice, 'voices[1].id' for a default female voice.
    # Note: You might need to enumerate the available voices on your system to find specific voice IDs.
    "voice": "default",

    # Optional. File path to save audio output, used by `engine.save_to_file`.
    # Example: 'test.mp3' to save output to a file named 'test.mp3'.
    "output_file_path": "test.mp3"
}

BROADCAST_CONFIG = {
    # Specifies the adapter class to be used for broadcasting functionality.
    # The value should be a string representing the module and class name of the broadcast adapter.
    # Example: "broadcast.adapters.websocket_server.WebSocketServer" for using WebSocket.
    #
    # Currently available adapters (defined in broadcast/adapters)):
    #  - broadcast.adapters.websocket_server.WebSocketServer
    #
    # Note: Additional custom adapters can be added to the broadcast/adapter directory. Next planned broadcaster is MQTT.
    "broadcast_adapter": "broadcast.adapters.websocket_server.WebSocketServer",
}

# broadcast.adapters.websocket_server.WebSocketServer configuration.
BROADCAST_WEBSOCKET_CONFIG={
    # The host address for the WebSocket server. 
    # 'localhost' refers to the local machine where the server is running.
    # This setting can be adjusted to a specific IP address or hostname if the server is accessible over a network.
    "websocket_host": "192.168.86.38",

    # The port number on which the WebSocket server will listen for incoming connections.
    # Port 8765 is used as a default value. This can be changed to any available port as needed.
    # Ensure that the selected port is not being used by other services and is open for network traffic if required.
    "websocket_port": 8765,
}
