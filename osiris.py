from config import AUDIO_SETTINGS, CELERY_CONFIG
from vosk import Model
from celery import Celery
from celery_config import get_celery_app
from database.setup import DatabaseSetup
from broadcast.broadcaster import broadcaster
from audio.audio_processor import AudioProcessor
from audio.audio_out import get_audio_out
from utils.os.helpers import OSHelper
from utils.text.welcome import welcome_message
from tools import * # Import all openai tool functions
import logging
import subprocess
import atexit
import sys
import threading
import time

from decorators.openai_decorators import openai_functions

# Configure basic logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    # Retrieve audio settings from the configuration file
    sound_device_samplerate = AUDIO_SETTINGS.get('SOUND_DEVICE_SAMPLERATE')
    vosk_model = Model(lang=AUDIO_SETTINGS.get('VOSK_MODEL', "en-us"))
    sound_device_device = AUDIO_SETTINGS.get('SOUND_DEVICE_DEVICE')
    sound_device_blocksize = AUDIO_SETTINGS.get('SOUND_DEVICE_BLOCK_SIZE', 28000)
    audio_in_dump_filename = AUDIO_SETTINGS.get('AUDIO_IN_DUMP_FILENAME')

    try: 
        # Initialize the audio processor with the configuration settings
        logging.info("ROBOT THOUGHT: I am ready to begin.")
        audio_processor = AudioProcessor(vosk_model, sound_device_samplerate, sound_device_device, sound_device_blocksize, audio_in_dump_filename, broadcaster)
        # Start processing the audio stream
        audio_processor.process_stream()
    except KeyboardInterrupt:
        # Log the termination of the process
        logging.info("\nDone")
    finally:
        # Terminate the Celery worker if it was started
        stop_celery_worker(celery_worker)
        audio_out.shutdown()
        broadcaster.shutdown()
        for thread in threading.enumerate():
            print(thread.name)
        sys.exit(0)

# Standard Python idiom for running the main function
if __name__ == "__main__":
    main()
