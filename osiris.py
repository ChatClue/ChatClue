from config import AUDIO_SETTINGS
from vosk import Model
from audio.audio_processor import AudioProcessor
import logging

# Configure basic logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to initiate the audio processing.
    Retrieves audio settings from the configuration and initializes the AudioProcessor.
    """
    # Retrieve audio settings from the configuration file
    sound_device_samplerate = AUDIO_SETTINGS.get('SOUND_DEVICE_SAMPLERATE')
    vosk_model = Model(lang=AUDIO_SETTINGS.get('VOSK_MODEL', "en-us"))
    sound_device_device = AUDIO_SETTINGS.get('SOUND_DEVICE_DEVICE')
    sound_device_blocksize = AUDIO_SETTINGS.get('SOUND_DEVICE_BLOCK_SIZE', 28000)
    audio_in_dump_filename = AUDIO_SETTINGS.get('AUDIO_IN_DUMP_FILENAME')


    try: 
        # Initialize the audio processor with the configuration settings
        audio_processor = AudioProcessor(vosk_model, sound_device_samplerate, sound_device_device, sound_device_blocksize, audio_in_dump_filename)
        
        # Start processing the audio stream
        audio_processor.process_stream()
    except KeyboardInterrupt:
        # Log the termination of the process
        logging.info("\nDone")

# Standard Python idiom for running the main function
if __name__ == "__main__":
    main()
