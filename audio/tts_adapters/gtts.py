from google.cloud import texttospeech
import uuid
import os
from config import GOOGLE_TTS_CONFIG

class GTTSAdapter:
    """
    Adapter class for Google Text-to-Speech (GTTS) service.

    This class abstracts the details of using the Google Text-to-Speech API
    to convert text into spoken audio.
    """

    def __init__(self):
        """
        Initializes the GTTSAdapter with Google Cloud credentials and API client.
        """
        if 'api_key_path' in GOOGLE_TTS_CONFIG:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_TTS_CONFIG['api_key_path']
        self.client = texttospeech.TextToSpeechClient()

        self.voice_model = GOOGLE_TTS_CONFIG.get('voice_model', 'en-US-Wavenet-D')
        self.language_code = GOOGLE_TTS_CONFIG.get('language_code', 'en-US')
        self.speaking_rate = GOOGLE_TTS_CONFIG.get('speaking_rate', 1.0)
        self.pitch = GOOGLE_TTS_CONFIG.get('pitch', 0)
        self.volume_gain_db = GOOGLE_TTS_CONFIG.get('volume_gain_db', 0)
        self.audio_encoding = GOOGLE_TTS_CONFIG.get('audio_encoding', texttospeech.AudioEncoding.LINEAR16)

    def synthesize_speech(self, text):
        """
        Converts text to speech.

        Args:
            text (str): The text to be synthesized into speech.

        Returns:
            str: Filename of the generated audio file.
        """
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=self.language_code, name=self.voice_model)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=self.audio_encoding,
            speaking_rate=self.speaking_rate,
            pitch=self.pitch,
            volume_gain_db=self.volume_gain_db
        )

        response = self.client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        filename = f"tmp/audio/temp_audio_{uuid.uuid4()}.wav"
        with open(filename, 'wb') as out:
            out.write(response.audio_content)
        return filename
