from google.cloud import texttospeech
from config import GOOGLE_TTS_CONFIG
from utils.os.helpers import OSHelper
import os
import pygame
import queue
import threading
import time
import logging
import uuid

class AudioOutput:
    """
    Manages the output of audio using Google Text-to-Speech and pygame for playback.

    This class handles converting text to speech, queuing speech for playback, and playing audio files sequentially.
    """
    def __init__(self):
        """
        Initializes the AudioOutput class with Google Cloud Text-to-Speech and pygame mixer settings.
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

        self.request_queue = queue.Queue()
        self.ready_files = queue.Queue()
        self.audio_thread = threading.Thread(target=self.process_queue)
        self.audio_thread.daemon = True
        self.audio_thread.start()

        self.play_thread = threading.Thread(target=self.play_sequentially)
        self.play_thread.daemon = True
        self.play_thread.start()

        self.tts_lock = threading.Lock()
        self.play_lock = threading.Lock()

    def text_to_speech(self, text):
        """
        Converts text to speech using Google's Text-to-Speech API.

        Args:
            text (str): The text to be converted to speech.

        Returns:
            str: The filename of the generated audio file.
        """
        # Generate the speech synthesis request
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=self.language_code, name=self.voice_model)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=self.audio_encoding,
            speaking_rate=self.speaking_rate,
            pitch=self.pitch,
            volume_gain_db=self.volume_gain_db
        )

        # Perform the text-to-speech request
        response = self.client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        # Create a unique filename for the audio file
        filename = f"tmp/audio/temp_audio_{uuid.uuid4()}.wav"

        # Save the synthesized speech to an audio file
        with open(filename, 'wb') as out:
            out.write(response.audio_content)
        return filename
    
    def add_to_queue(self, text):
        """
        Adds text to the queue for speech synthesis and playback.

        Args:
            text (str): The text to be converted to speech and played.
        """
        self.request_queue.put(text)

    def process_queue(self):
        """
        Continuously processes items from the request queue, converting them to speech.
        """
        while True:
            text = self.request_queue.get()
            with self.tts_lock:
                filename = self.text_to_speech(text)
                self.ready_files.put(filename)
                self.request_queue.task_done()
    
    def play_sequentially(self):
        """
        Continuously plays audio files from the ready files queue, sequentially.
        """
        while True:
            if not self.is_playing() and not self.ready_files.empty():
                filename = self.ready_files.get()
                with self.play_lock:
                    # Check if the file exists and retry a few times if it doesn't
                    for _ in range(100):  # retry up to 3 times
                        if os.path.exists(filename):
                            self.play_audio_file(filename)
                            break
                        time.sleep(0.1)  # wait for 100 milliseconds before retrying

    def is_playing(self):
        """
        Checks if there is currently audio being played.

        Returns:
            bool: True if audio is currently playing, False otherwise.
        """
        return pygame.mixer.music.get_busy()

    def play_audio_file(self, filename):
        """
        Plays an audio file using pygame's mixer.

        Args:
            filename (str): The filename of the audio file to be played.
        """
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            # Wait until the audio playback is finished
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            # Remove the audio file after playing
            if os.path.exists(filename):
                os.remove(filename)
        except pygame.error as e:
            logging.error(f"Error playing audio file: {e}")

    def stop_audio(self):
        """
        Stops any ongoing audio playback.
        """
        pygame.mixer.music.stop()
    
    def stop_all_audio(self):
        """
        Stops all audio playback and clears the audio queues.
        """
        self.clear_queue()
        self.stop_audio()
        OSHelper.clear_orphaned_audio_files()

    def clear_queue(self):
        """
        Clears all items from the audio request and ready files queues.
        """
        while not self.request_queue.empty():
            try:
                self.request_queue.get_nowait()  # Remove all items from the queue
                self.request_queue.task_done()
            except queue.Empty:
                break
        while not self.ready_files.empty():
            try:
                self.ready_files.get_nowait()  # Remove all items from the queue
                self.ready_files.task_done()
            except queue.Empty:
                break

audio_out = AudioOutput()

def get_audio_out():
    """
    Returns the instance of AudioOutput for use.

    Returns:
        AudioOutput: The instance of the AudioOutput class.
    """
    return audio_out