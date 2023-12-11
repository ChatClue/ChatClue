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
    "WAKE_PHRASES": ["robot"],
    "SOUND_DEVICE_SAMPLERATE": 48000,
    "AUDIO_IN_DUMP_FILENAME": "output.wav",
    "VOSK_MODEL": "en-us",
    "SOUND_DEVICE_BLOCK_SIZE": 28000,
    "SOUND_DEVICE_DEVICE": "default"
}

OPENAI_SETTINGS = {
    #"api_key": "sk-<your-openai-api-key>", # Optional. An OPENAI_API_KEY environment variable is also supported.
    "model": "gpt-3.5-turbo",
    "embedding_model": "text-embedding-ada-002"
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