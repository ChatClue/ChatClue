from config import TTS_CONFIG
from utils.os.helpers import OSHelper
import importlib
import os
import pygame
import queue
import threading
import time
import logging

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

        self.stop_signal = threading.Event()

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
        self.request_queue.put(text)

    def process_queue(self):
        """
        Continuously processes items from the request queue, converting them to speech.
        """
        while not self.stop_signal.is_set():
            try:
                text = self.request_queue.get(timeout=0.1)
                with self.tts_lock:
                    if not self.stop_signal.is_set():
                        filename = self.text_to_speech(text)
                        self.ready_files.put(filename)
                        self.request_queue.task_done()
                    else: 
                        break
            except queue.Empty:
                continue
    
    def play_sequentially(self):
        while not self.stop_signal.is_set():
            if not self.is_playing() and not self.ready_files.empty():
                filename = self.ready_files.get()
                with self.play_lock:
                    if not self.stop_signal.is_set():  # Check again before playing
                        # Check if the file exists and retry a few times if it doesn't
                        for _ in range(3):  # retry up to 3 times
                            if os.path.exists(filename):
                                self.play_audio_file(filename)
                                break
                            time.sleep(0.1)  # wait for 100 milliseconds before retrying
                    else:
                        break

    def is_playing(self):
        """
        Checks if there is currently audio being played.

        Returns:
            bool: True if audio is currently playing, False otherwise.
        """
        if pygame.mixer.get_init():
            return pygame.mixer.music.get_busy()
        else:
            return False

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
        self.full_clear()
        time.sleep(0.5)
        self.full_clear()
        
    def full_clear(self):
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
    
    def shutdown(self):
        # Signal the threads to stop running
        self.stop_signal.set()
        self.stop_all_audio()
        logging.info("AUDIO STOPPED")

audio_out = AudioOutput()

def get_audio_out():
    """
    Returns the instance of AudioOutput for use.

    Returns:
        AudioOutput: The instance of the AudioOutput class.
    """
    return audio_out