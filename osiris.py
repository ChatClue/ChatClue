from config import AUDIO_SETTINGS
from vosk import Model
from audio.audio_processor import AudioProcessor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    sound_device_samplerate = AUDIO_SETTINGS['SOUND_DEVICE_SAMPLERATE'] if AUDIO_SETTINGS['SOUND_DEVICE_SAMPLERATE'] is not None else None
    vosk_model = Model(lang=AUDIO_SETTINGS['VOSK_MODEL'] if AUDIO_SETTINGS['VOSK_MODEL'] is not None else "en-us")
    sound_device_device = AUDIO_SETTINGS['SOUND_DEVICE_DEVICE'] if AUDIO_SETTINGS['SOUND_DEVICE_DEVICE'] is not None else None
    sound_device_blocksize = AUDIO_SETTINGS['SOUND_DEVICE_BLOCK_SIZE'] if AUDIO_SETTINGS['SOUND_DEVICE_BLOCK_SIZE'] is not None else 28000
    audio_in_dump_filename = AUDIO_SETTINGS['AUDIO_IN_DUMP_FILENAME'] if AUDIO_SETTINGS['AUDIO_IN_DUMP_FILENAME'] is not None else None

    try: 
        audio_processor = AudioProcessor(vosk_model, sound_device_samplerate, sound_device_device, sound_device_blocksize, audio_in_dump_filename)
        audio_processor.process_stream()
    except KeyboardInterrupt:
        logging.info("\nDone")

if __name__ == "__main__":
    main()
