from google.cloud import texttospeech
from config import GOOGLE_TTS_CONFIG
import os
import pygame
import queue
import threading

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

        self.request_queue = queue.Queue()
        self.audio_thread = threading.Thread(target=self.process_queue)
        self.audio_thread.daemon = True
        self.audio_thread.start()

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
    
    def add_to_queue(self, text):
        self.request_queue.put(text)

    def process_queue(self):
        while True:
            text = self.request_queue.get()
            if not self.is_playing():
                self.text_to_speech(text)
            self.request_queue.task_done()

    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def play_audio(self, audio_content):
        if not audio_content:
            print("Received empty audio content.")
            return

        filename = "temp_audio_output.wav"
        with open(filename, 'wb') as out:
            out.write(audio_content)

        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except pygame.error as e:
            print(f"Error playing audio file: {e}")

        os.remove(filename)

    def stop_audio(self):
        # Stops any ongoing audio playback
        pygame.mixer.music.stop()
    
    def stop_all_audio(self):
        self.clear_queue()
        self.stop_audio()

    def clear_queue(self):
        while not self.request_queue.empty():
            try:
                self.request_queue.get_nowait()  # Remove all items from the queue
                self.request_queue.task_done()
            except queue.Empty:
                break
