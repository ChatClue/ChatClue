import pyttsx3
import uuid
import os
from config import PYTTSX3_TTS_CONFIG

class Pyttsx3Adapter:
    """
    Adapter class for pyttsx3, a text-to-speech library for Python.
    This class abstracts the details of using the pyttsx3 library
    to convert text into spoken audio.
    """

    def __init__(self):
        """
        Initializes the Pyttsx3Adapter with configuration settings.
        """
        self.engine = pyttsx3.init()

        # Apply configuration settings
        self.engine.setProperty('rate', PYTTSX3_TTS_CONFIG['rate'])
        self.engine.setProperty('volume', PYTTSX3_TTS_CONFIG['volume'])
        if PYTTSX3_TTS_CONFIG['voice'] != 'default':
            voices = self.engine.getProperty('voices')
            # Assuming 'voice' is an index; adjust logic if it's an ID or name
            self.engine.setProperty('voice', voices[PYTTSX3_TTS_CONFIG['voice']].id)
    
    # This is not used by AudioOutput and is not a required function of a TTS Adapter for Osiris. This is just added here as a helper function if needed.
    def list_available_voices(self):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for i, voice in enumerate(voices):
            print(f"Voice {i}:")
            print(f" - ID: {voice.id}")
            print(f" - Name: {voice.name}")
            print(f" - Languages: {voice.languages}")
            print(f" - Gender: {voice.gender}")
            print(f" - Age: {voice.age}")
            print("")

    def synthesize_speech(self, text):
        """
        Converts text to speech using the pyttsx3 library.

        Args:
            text (str): The text to be synthesized into speech.

        Returns:
            str: Filename of the generated audio file.
        """
        filename = f"tmp/audio/temp_audio_{uuid.uuid4()}.wav"
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()  # Blocks while processing all currently queued commands
        return filename
