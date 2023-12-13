import os
from celery import shared_task
from audio.audio_out import AudioOutput

audio_output = AudioOutput()

@shared_task(bind=True)
def play_audio_task(self, text):
    filename = "temp_audio_output.wav"

    # Check if the audio file exists, implying audio is currently being played
    if os.path.exists(filename):
        # Requeue the task with a delay
        self.retry(countdown=2)
        return

    # If audio is not being played, proceed to play the new text
    audio_output = AudioOutput()
    audio_output.text_to_speech(text)

    