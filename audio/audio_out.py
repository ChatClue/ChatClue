from config import TTS_CONFIG
from utils.os.helpers import OSHelper
import importlib
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
        Initializes the AudioOutput class with a dynamically selected TTS adapter, required threads, and pygame mixer settings.
        """
        tts_adapter_path = TTS_CONFIG['tts_adapter']
        tts_module_name, tts_class_name = tts_adapter_path.rsplit(".", 1)
        tts_module = importlib.import_module(tts_module_name)
        tts_adapter_class = getattr(tts_module, tts_class_name)
        self.tts_adapter = tts_adapter_class()  # Instantiate the TTS adapter
        self.interruption_detected = False 

        self.running = True

        # Initialize pygame for playing audio
        pygame.init()
        pygame.mixer.init() 

        # Instantiate incoming text request_queue and outgoing audio ready_files queue.
        self.request_queue = queue.Queue()
        self.ready_files = queue.Queue()

        # Create a thread to handle the incoming text process_queue
        self.audio_thread = threading.Thread(target=self.process_queue)
        self.audio_thread.daemon = True
        self.audio_thread.start()

        # Create a thread to handle the outgoing audio ready_files
        self.play_thread = threading.Thread(target=self.play_sequentially)
        self.play_thread.daemon = True
        self.play_thread.start()

        # Create locks for the process_queue and play threads
        self.tts_lock = threading.Lock()
        self.play_lock = threading.Lock()

    def text_to_speech(self, text):
        """
        Converts text to speech using the configured TTS service.

        Args:
            text (str): The text to be converted to speech.

        Returns:
            str: The filename of the generated audio file.
        """
        return self.tts_adapter.synthesize_speech(text)
    
    def add_to_queue(self, text):
        """
        Adds text to the queue for speech synthesis and playback.

        Args:
            text (str): The text to be converted to speech and played.
        """
        self.interruption_detected = False
        self.request_queue.put(text)

    def process_queue(self):
        """
        Continuously processes items from the request queue, converting them to speech.
        """
        while self.running and not self.interruption_detected:
            text = self.request_queue.get()
            with self.tts_lock:
                filename = self.text_to_speech(text)
                if not self.interruption_detected:
                    self.ready_files.put(filename)
                self.request_queue.task_done()
    
    def play_sequentially(self):
        """
        Continuously plays audio files from the ready files queue, sequentially.
        """
        while self.running:
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
        self.interruption_detected = True
        self.clear_queue()
        self.stop_audio()
        OSHelper.clear_orphaned_audio_files()
        time.sleep(1)
        self.interruption_detected = False

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
    
    def shutdown(self):
        self.stop_all_audio()
        # Signal the threads to stop running
        self.running = False

audio_out = AudioOutput()

def get_audio_out():
    """
    Returns the instance of AudioOutput for use.

    Returns:
        AudioOutput: The instance of the AudioOutput class.
    """
    return audio_out