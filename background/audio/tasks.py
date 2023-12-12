# from celery import shared_task
# from audio.audio_out import AudioOutput

# audio_output = AudioOutput()

# @shared_task
# def play_audio_task(sentence):
#     if audio_output.is_playing:
#         # Re-queue task with a delay if audio is currently playing
#         play_audio_task.apply_async(args=[sentence], countdown=1)
#     else:
#         audio_output.queue_sentence(sentence)
