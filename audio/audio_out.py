from google.cloud import texttospeech
from celery import Celery
from celery_config import get_celery_app
from config import GOOGLE_TTS_CONFIG
import os
import pygame

class AudioOutput:
    def __init__(self):
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
        # Synthesize speech from the text
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=self.language_code, name=self.voice_model)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=self.audio_encoding,
            speaking_rate=self.speaking_rate,
            pitch=self.pitch,
            volume_gain_db=self.volume_gain_db
        )

        response = self.client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        # Play the synthesized audio
        self.play_audio(response.audio_content)

    def play_audio(self, audio_content):
        # Save and play audio content
        filename = "temp_audio_output.wav"
        with open(filename, 'wb') as out:
            out.write(audio_content)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Optionally, delete the temporary audio file here
        os.remove(filename)

    def stop_audio(self):
        # Stops any ongoing audio playback
        pygame.mixer.music.stop()
    
    def stop_all_audio(self):
        self.stop_audio_flag = True
        self.stop_audio()
        get_celery_app().control.purge()  # Purging Celery tasks
