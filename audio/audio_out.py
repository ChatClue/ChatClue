from google.cloud import texttospeech
from config import GOOGLE_TTS_CONFIG
import os
import pygame

class AudioOutput:
    """
    A class to handle text-to-speech conversion and playback using Google Cloud Text-to-Speech API and pygame.

    Attributes:
        client (TextToSpeechClient): Google Cloud Text-to-Speech client.
        voice_model (str): The voice model to use for speech synthesis.
        language_code (str): The language code for the voice model.
        speaking_rate (float): The rate at which the text should be spoken.
        pitch (float): The pitch of the synthesized speech.
        volume_gain_db (float): The volume gain for the synthesized speech.
        audio_encoding (AudioEncoding): The audio format for the synthesized speech.
    """

    def __init__(self):
        """
        Initializes the AudioOutput class with Google Cloud Text-to-Speech client and pygame mixer.
        """
        # Set Google Cloud credentials if provided via config
        if 'api_key_path' in GOOGLE_TTS_CONFIG:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_TTS_CONFIG['api_key_path']

        # Initialize Google Cloud Text-to-Speech client
        self.client = texttospeech.TextToSpeechClient()

        # Initialize pygame for playing audio
        pygame.init()
        pygame.mixer.init()

        # Configuration settings
        self.voice_model = GOOGLE_TTS_CONFIG.get('voice_model', 'en-US-Wavenet-D')
        self.language_code = GOOGLE_TTS_CONFIG.get('language_code', 'en-US')
        self.speaking_rate = GOOGLE_TTS_CONFIG.get('speaking_rate', 1.0)
        self.pitch = GOOGLE_TTS_CONFIG.get('pitch', 0)
        self.volume_gain_db = GOOGLE_TTS_CONFIG.get('volume_gain_db', 0)
        self.audio_encoding = GOOGLE_TTS_CONFIG.get('audio_encoding', texttospeech.AudioEncoding.LINEAR16)

    def text_to_speech(self, text):
        """
        Converts the given text to speech using Google Cloud Text-to-Speech API and plays it.

        Args:
            text (str): The text to be converted to speech.
        """
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request, select the language code and voice model
        voice = texttospeech.VoiceSelectionParams(
            language_code=self.language_code,
            name=self.voice_model
        )

        # Select the type of audio file
        audio_config = texttospeech.AudioConfig(
            audio_encoding=self.audio_encoding,
            speaking_rate=self.speaking_rate,
            pitch=self.pitch,
            volume_gain_db=self.volume_gain_db
        )

        # Perform the text-to-speech request on the text input with the selected voice parameters and audio file type
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config)

        # Play the synthesized audio
        self.play_audio(response.audio_content)

    def play_audio(self, audio_content):
        """
        Plays the given audio content using pygame mixer.

        Args:
            audio_content (bytes): The audio content to be played.
        """
        # Save the audio content to a file
        filename = "temp_audio_output.wav"
        with open(filename, 'wb') as out:
            out.write(audio_content)

        # Load and play the audio file
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Optionally, delete the temporary audio file here
        os.remove(filename)
