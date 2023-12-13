import queue
import logging
import json
import threading
import time
import sounddevice as sd
from vosk import KaldiRecognizer
from .audio_out import AudioOutput
from integrations.openai import OpenAIClient
from integrations.openai_conversation_builder import OpenAIConversationBuilder
from utils.audio_helpers import contains_quiet_please_phrase, contains_wake_phrase
from background.memory.tasks import store_conversation_task
from database.conversations import ConversationMemoryManager
from config import CONVERSATIONS_CONFIG

class AudioProcessor:
    """
    A class to handle audio processing, including capturing audio input, 
    processing it with Vosk for speech recognition, and responding using OpenAI's GPT model.

    Attributes:
        model (Vosk.Model): Vosk speech recognition model.
        samplerate (int): The sample rate for audio capture.
        device (str): The name of the audio input device.
        blocksize (int): The block size for audio processing.
        dump_filename (str): Filename to dump the audio input, if provided.
    """

    def __init__(self, model, samplerate, device, blocksize, dump_filename=None):
        self.model = model
        self.samplerate = samplerate
        self.device = device
        self.blocksize = blocksize
        self.dump_filename = dump_filename
        self.audio_queue = queue.Queue()
        self.openai_client = OpenAIClient()
        self.conversation_memory_manager = ConversationMemoryManager()
        self.openai_conversation_builder = OpenAIConversationBuilder()
        self.audio_out = AudioOutput()
        self.audio_out_response_buffer = ''
        self.full_assistant_response = ''
        self.last_wake_time = 0
        self.last_response_end_time = 0

    def open_dump_file(self):
        """Opens the file to dump audio input if a filename is provided."""
        if self.dump_filename is not None:
            self.dump_filename = open(self.dump_filename, "wb")

    def close_dump_file(self):
        """Closes the audio dump file if it was opened."""
        if self.dump_filename is not None:
            self.dump_filename.close()

    def should_process(self, result, current_time):
        """
        Determines whether the robot should process the input based on wake phrases or elapsed time.

        Args:
            result (str): The recognized text from the audio input.
            current_time (float): The current time in seconds.

        Returns:
            bool: True if the input should be processed, False otherwise.
        """
        return (not contains_quiet_please_phrase(result) and contains_wake_phrase(result)) or \
               (not contains_quiet_please_phrase(result) and (current_time - self.last_wake_time <= 10) or (current_time - self.last_response_end_time <= 10) and not self.audio_out.is_playing)  \

    def update_wake_time(self):
        """Updates the time when a wake phrase was last heard."""
        self.last_wake_time = time.time()

    def update_response_end_time(self):
        """Updates the time when the robot's last response ended."""
        self.last_response_end_time = time.time()

    def callback(self, indata, frames, time, status):
        """
        Callback function for audio input stream.

        Args:
            indata: The buffer containing the incoming sound.
            frames: The number of frames.
            time: Current stream time.
            status: Status of the stream.
        """
        if status:
            logging.warning(status)
        self.audio_queue.put(bytes(indata))

    def process_stream(self):
        """
        Starts the audio processing stream, listens for speech, and processes it.
        """
        self.open_dump_file()
        try:
            with sd.RawInputStream(samplerate=self.samplerate, blocksize=self.blocksize, device=self.device,
                                dtype="int16", channels=1, callback=self.callback):
                rec = KaldiRecognizer(self.model, self.samplerate)
                openai_stream_thread = None

                while True:
                    current_time = time.time()
                    data = self.audio_queue.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())["text"]
                        if result != '' and result != 'huh':
                            logging.info("ROBOT HEARD: " + result)
                            if self.should_process(result, current_time):
                                self.update_wake_time()
                                if not openai_stream_thread or not openai_stream_thread.is_alive():
                                    self.openai_client.stop_signal.clear()
                                    conversation = self.openai_conversation_builder.create_recent_conversation_messages_array(result)
                                    openai_stream_thread = threading.Thread(target=self.openai_client.stream_response, args=(conversation,))
                                    openai_stream_thread.start()
                                    logging.info("ROBOT ACTION: Comitting user input to memory.")
                                    self.store_conversation(speaker_type=CONVERSATIONS_CONFIG["user"], response=result)
                            else:
                                logging.info("ROBOT THOUGHT: Ignoring Conversation, it doesn't appear to be relevant.")

                    partial_result_json = json.loads(rec.PartialResult())
                    if 'partial' in partial_result_json and contains_quiet_please_phrase(partial_result_json['partial']):
                        logging.info("ROBOT THOUGHT: Request to stop talking recognized. Stopping stream.")
                        #stopping openai api stream
                        self.openai_client.stop_signal.set()
                        with self.openai_client.response_queue.mutex:
                            self.openai_client.response_queue.queue.clear()
                            if self.full_assistant_response:
                                logging.info("ROBOT ACTION: Comitting my partial response to memory")
                                self.store_full_assistant_response()
                        #stopping audio output
                        logging.info("ROBOT ACTION: Stopping audio output.")
                        self.audio_out.stop_all_audio()

                    if self.dump_filename is not None:
                        self.dump_filename.write(data)

                    while not self.openai_client.response_queue.empty():
                        chunk = self.openai_client.response_queue.get()
                        if chunk.choices[0].delta.content is not None:
                            response_text = chunk.choices[0].delta.content
                            print(response_text, end='', flush=True)    
                            self.update_response_end_time()
                            # Play audio associated with this chunk via our TTS
                            # Append to buffer
                            self.audio_out_response_buffer += response_text
                            # Check if buffer ends with a sentence
                            if self.audio_out_response_buffer.endswith(('.', '?', '!')):
                                # Queue the complete sentence for audio output
                                self.audio_out.add_to_queue(self.audio_out_response_buffer)
                                # Clear the buffer
                                self.audio_out_response_buffer = ""
                            # Append this chunk to the full response
                            self.full_assistant_response += response_text
                    
                    if self.full_assistant_response and self.openai_client.streaming_complete:
                        # Commit the full response to memory
                        logging.info("ROBOT ACTION: Comitting my full response to memory")
                        self.store_full_assistant_response()
                        

                        
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            self.close_dump_file()

    def store_full_assistant_response(self):
        """
        Stores the full assistant response in the database.
        """
        self.store_conversation(speaker_type=CONVERSATIONS_CONFIG["assistant"], response=self.full_assistant_response)
        self.full_assistant_response = ''

    def store_conversation(self, speaker_type, response):
        """
        Stores the conversation part in the database asynchronously using a Celery task.

        Args:
            speakerType (str): "user" or "assistant", indicating who is speaking.
            response (str): The text of the response.
        """
        store_conversation_task.delay(speaker_type=speaker_type, response=response)
