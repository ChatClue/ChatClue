AUDIO_SETTINGS = {
    "QUIET_PLEASE_PHRASES": [
        "be noiseless", "button it", "calm your voice", "cease speaking", 
        "cease your chatter", "close your mouth", "cut it out", "don't speak", 
        "end the noise", "enough", "go mute", "hush", "hush down", 
        "hush now", "keep quiet", "keep it down", "keep the silence", "mums the word", 
        "mute", "muzzle it", "no chit chat", "no more words", "no talking", 
        "not another word", "please stop", "put a lid on it", "quiet", "quietude", 
        "shh", "shhh", "shut up", "silence", "silence yourself", "silence your lips", 
        "speechless", "sshh", "stay mum", "stifle your speech", "stop", "stop babbling", 
        "stop blabbering", "stop talking", "tone it down"
    ],
    "WAKE_PHRASES": ["robot", "computer"],
    "SOUND_DEVICE_SAMPLERATE": 48000,
    "AUDIO_IN_DUMP_FILENAME": "output.wav",
    "VOSK_MODEL": "en-us",
    "SOUND_DEVICE_BLOCK_SIZE": 28000,
    "SOUND_DEVICE_DEVICE": "default"
}

OPENAI_SETTINGS = {
    #"api_key": "sk-<your-openai-api-key>", # Optional. An OPENAI_API_KEY environment variable is also supported.
    "model": "gpt-3.5-turbo", #"gpt-4-1106-preview",
    "embedding_model": "text-embedding-ada-002",
    "max_context_tokens": 2500,
    "initial_system_message": "You are a friendly, but not obsequious, robot assistant that provides all output in SSML format that closely conveys the intonations and emotion that you might guess a human would have speaking the same words. This output will then be used by a TTS system.", #Optional.
}

DATABASE_CONFIG = {
    'dbname': 'conversations',
    'user': 'postgres',
    'password': '',
    'host': 'localhost',  
    'port': '5432'  
}

CONVERSATIONS_CONFIG = {
    "user": 1,
    "assistant": 2
}

CELERY_CONFIG = {
    "RUN_LOCALLY_AUTOMATICALLY": True, # Set to False if you want to start celery manually `celery -A osiris.celery_app worker --loglevel=info` or if celery is running separately. True is best for development enviornments.
    "LOCAL_LOG_LEVEL": "info", # Set to "debug" for more verbose logging.
    "APPLICATION_NAME": "osiris",
    "BROKER_URL": 'redis://localhost:6379/0'
}

GOOGLE_TTS_CONFIG = {
    #'api_key_path': 'path/to/api_key.json',  # Optional. Assumes you are not using the GOOGLE_APPLICATION_CREDENTIALS environment variable. Path to the JSON file containing your Google Cloud API key
    'voice_model': 'en-US-Wavenet-D',  # Optional. Voice model to use (e.g., 'en-US-Wavenet-D')
    'language_code': 'en-US',  # Optional. Language code (e.g., 'en-US' for American English)
    'speaking_rate': 1.0,  # Optional. Default Speaking rate, 1.0 is normal, can range between 0.25 and 4.0. Robot may change this dynamically depending on the context of the conversation.
    'pitch': 0,  # Optional. Pitch, can range from -20.0 to 20.0, 0 is the default pitch. Robot can modify.
    'volume_gain_db': 0,  # Optional. Volume gain in dB, can range from -96.0 to 16.0, 0 is the default. Robot can modify.
    'audio_encoding': 'LINEAR16',  # Optional. The audio encoding of the output file (e.g., 'LINEAR16', 'MP3', 'OGG_OPUS')
}
