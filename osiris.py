from config import CELERY_CONFIG, LOG_LEVEL, VIDEO_SETTINGS
from utils.os.helpers import OSHelper
from celery import Celery
from celery_config import get_celery_app
from database.setup import DatabaseSetup
from broadcast.broadcaster import broadcaster
from audio.audio_processor import AudioProcessor
from video.video_processor import VideoProcessor
from audio.audio_out import get_audio_out
from utils.os.helpers import OSHelper
from utils.text.welcome import welcome_message
from utils.logging.colors import ColorFormatter
from background.memory.tasks import *
from tools import * # Import all openai tool functions
import logging
import subprocess
import atexit
import sys
import threading
import time
import cv2
import queue

# Configure basic logging for the application
logging.basicConfig(level=LOG_LEVEL)
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s - %(message)s'))

# Ensure the necessary tmp/ directories exist
OSHelper.configure_tmp_directories()

# Configure background processor / subconcious systems
celery_app = get_celery_app()

# Configure audio output
audio_out = get_audio_out()

def start_celery_worker():
    """
    Starts a Celery worker as a subprocess.

    This method initiates a Celery worker using the subprocess module. The worker runs asynchronously 
    and executes tasks defined in the Celery application. The worker is configured to log at the 
    'info' level for better visibility of its operations.

    The function also ensures that the Celery worker is terminated gracefully when the Python script exits. 
    This is achieved using the `atexit` module, which registers a function to terminate the worker 
    as part of the script's cleanup process.

    Returns:
        subprocess.Popen: The subprocess object representing the Celery worker.
    """
    # Get the log level from configuration, default to 'info'
    log_level = CELERY_CONFIG.get('LOCAL_LOG_LEVEL', 'info')
    # Start Celery worker
    celery_worker = subprocess.Popen(['celery', '-A', 'osiris.celery_app', 'worker', f'--loglevel={log_level}'])
    # Register function to terminate worker on exit
    atexit.register(lambda: celery_worker.terminate())
    return celery_worker

def stop_celery_worker(celery_worker):
    """
    Stops the Celery worker gracefully.

    Args:
        celery_worker (subprocess.Popen): The subprocess object representing the Celery worker.
    """
    if celery_worker:
        # Send SIGTERM signal to gracefully terminate the worker
        celery_worker.terminate()
        # Wait for the worker to exit
        try:
            celery_worker.wait(timeout=0.5)  # Adjust the timeout as needed
        except subprocess.TimeoutExpired:
            # If the worker doesn't terminate within the timeout, kill it
            logging.info("Forcibly terminating the Celery worker.")
            celery_worker.kill()


def main():
    """
    Main function to initialize the application.
    Configures celery background worker, database, broadcaster, and audio settings.
    """
    welcome_message()
    # Optionally start Celery worker
    celery_worker = None
    if CELERY_CONFIG.get("RUN_LOCALLY_AUTOMATICALLY", True):
        logging.info("ROBOT THOUGHT: Starting subconscious systems locally")
        celery_worker = start_celery_worker()
        logging.info("ROBOT THOUGHT: Subconscious systems activated")

    # Setup the database
    DatabaseSetup.initial_setup()

    try: 
        # Initialize the audio processor with the configuration settings
        logging.info("ROBOT THOUGHT: I am ready to begin.")
        audio_out.add_to_queue("Welcome to Chat Clue's Project Osiris. I am ready to begin.")
        # Start Audio processing
        audio_processor = AudioProcessor()
        audio_thread = threading.Thread(target=audio_processor.process_stream)
        audio_thread.start()
        # Start Video processing
        video_processor = VideoProcessor()
        video_thread = threading.Thread(target=video_processor.process_stream)
        video_thread.start()
        # Keep the main thread alive
        try:
            while True:
                try:
                    if VIDEO_SETTINGS.get('SHOW_VIDEO', False):
                        frame = video_processor.frame_queue.get(timeout=0.1)
                        cv2.imshow('Processed Video Stream', frame)
                        if cv2.waitKey(1) & 0xFF == 27:
                            break
                except queue.Empty:
                    pass 
        except KeyboardInterrupt:
            audio_processor.shutdown()
            video_processor.shutdown()
            logging.info("Program interrupted by user. Exiting...")
        
        audio_thread.join()
        video_thread.join()

    except KeyboardInterrupt:
        # Log the termination of the process
        logging.info("\nDone")
    finally:
        # Terminate the Celery worker if it was started
        stop_celery_worker(celery_worker)
        audio_out.shutdown()
        broadcaster.shutdown()
        OSHelper.system_file_cleanup()
        sys.exit(0)

# Standard Python idiom for running the main function
if __name__ == "__main__":
    main()
