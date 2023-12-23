import queue
import logging
import json
import threading
import time
import sounddevice as sd
from vosk import KaldiRecognizer
from .audio_out import get_audio_out
from integrations.openai.openai import OpenAIClient
from integrations.openai.openai_conversation_builder import OpenAIConversationBuilder
from utils.audio.helpers import contains_quiet_please_phrase, contains_wake_phrase, get_tool_not_found_phrase
from background.memory.tasks import store_conversation_task
from decorators.openai_decorators import openai_functions
from utils.openai.tool_processor import ToolProcessor
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

    def __init__(self, model, samplerate, device, blocksize, dump_filename=None, broadcaster=None):
        self.model = model
        self.samplerate = samplerate
        self.device = device
        self.blocksize = blocksize
        self.dump_filename = dump_filename
        self.audio_queue = queue.Queue()
        self.openai_client = OpenAIClient()
        self.conversation_memory_manager = ConversationMemoryManager()
        self.openai_conversation_builder = OpenAIConversationBuilder()
        self.tool_processor = ToolProcessor()
        self.broadcaster = broadcaster
        self.audio_out = get_audio_out()
        self.audio_out_response_buffer = ''
        self.full_assistant_response = ''
        self.last_wake_time = 0
        self.last_response_end_time = 0
        self.processing_openai_request = False

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
        Processes the audio stream by recognizing speech and generating responses.

        Continuously captures audio, performs speech recognition, and generates responses using OpenAI.
        """
        self.open_dump_file()
        try:
            with sd.RawInputStream(samplerate=self.samplerate, blocksize=self.blocksize, device=self.device,
                                   dtype="int16", channels=1, callback=self.callback):
                rec = KaldiRecognizer(self.model, self.samplerate)
                openai_stream_thread = None

                while True:
                    data, current_time = self.get_audio_data()
                    result = self.process_recognition(data, rec)

                    if result:
                        openai_stream_thread = self.handle_speech(result, openai_stream_thread, current_time)

                    self.handle_partial_results(rec)
                    self.write_to_dump_file(data)
                    self.process_openai_response()

        # except Exception as e:
        #     logging.error(f"An error occurred: {e}")
        finally:
            self.close_dump_file()

    def get_audio_data(self):
        """
        Retrieves audio data from the queue.

        Returns:
            tuple: A tuple containing the audio data and the current time.
        """
        data = self.audio_queue.get()
        current_time = time.time()
        return data, current_time

    def process_recognition(self, data, rec):
        """
        Processes the recognition of speech from audio data.

        Args:
            data: The audio data to be processed.
            rec (KaldiRecognizer): The Vosk recognizer instance.

        Returns:
            str or None: Recognized text or None if no significant speech is recognized.
        """
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())["text"]
            if result not in ['', 'huh']:
                self.broadcaster.send_message(result)
                logging.info("ROBOT HEARD: " + result)
                return result
        return None

    def handle_speech(self, result, openai_stream_thread, current_time):
        """
        Processes the recognized speech and determines the appropriate response.

        Args:
            result (str): Recognized speech text.
            openai_stream_thread (threading.Thread): The current OpenAI stream thread.
            current_time (float): Current time in seconds.

        Returns:
            threading.Thread: Updated or new OpenAI stream thread.
        """
        try:
            if self.should_process(result, current_time) and not self.processing_openai_request:
                self.update_wake_time()
                self.processing_openai_request = True
                if not openai_stream_thread or not openai_stream_thread.is_alive():
                    self.openai_client.stop_signal.clear()
                    is_tool_request, conversation = self.determine_tool_request(result)
                    if is_tool_request:
                        self.handle_tool_request(result, conversation)
                    else:
                        self.continue_conversation(result, conversation)
            else:
                logging.info("ROBOT THOUGHT: Ignoring Conversation, it doesn't appear to be relevant.")
        finally:
            self.processing_openai_request = False
            return openai_stream_thread
        
    
    def determine_tool_request(self, result):
        """
        Determines whether the given input text is a tool request.

        Args:
            result (str): The recognized text to evaluate.

        Returns:
            Tuple[bool, list]: A tuple containing a boolean indicating whether it's a tool request, 
                               and the conversation array for further processing.
        """
        call_type_messages = self.openai_conversation_builder.create_check_if_tool_call_messages(result)
        openai_is_tool_response = self.openai_client.create_completion(call_type_messages, False, {"type": "json_object"}, openai_functions, True)
        
        is_tool_request = False
        conversation = self.openai_conversation_builder.create_recent_conversation_messages_array(result)

        try:
            if openai_is_tool_response and openai_is_tool_response.choices:
                is_tool_request = json.loads(openai_is_tool_response.choices[0].message.content).get("is_tool", False)
        except (TypeError, AttributeError, json.JSONDecodeError):
            print("Error parsing OpenAI response or response not in expected format.")

        return is_tool_request, conversation

    def handle_tool_request(self, result, conversation):
        """
        Handles the processing of a tool request.

        Args:
            result (str): The recognized text.
            conversation (list): The conversation array built up to this point.
        """
        tool_response = self.openai_client.create_completion(conversation, False, None, openai_functions)
        tool_response_message = tool_response.choices[0].message 
        tool_calls = tool_response_message.tool_calls  
        if tool_calls:
            self.process_tool_calls(tool_calls, result, conversation, tool_response_message)
        else:
            self.continue_conversation(result, conversation)

    def process_tool_calls(self, tool_calls, result, conversation, tool_response_message):
        """
        Processes the tool calls received from OpenAI.

        Args:
            tool_calls (list): List of tool calls from OpenAI response.
            result (str): The recognized text.
            conversation (list): The conversation array.
            tool_response_message (Message): The tool response message from OpenAI.
        """
        tool_call = tool_calls[0]
        tool_processor_response = self.tool_processor.process_tool_request(tool_call)
        if tool_processor_response["success"]:
            self.handle_successful_tool_response(tool_processor_response, result, conversation, tool_response_message)
        else:
            self.audio_out.add_to_queue(get_tool_not_found_phrase())

    def handle_successful_tool_response(self, tool_processor_response, result, conversation, tool_response_message):
        """
        Handles a successful tool response.

        Args:
            tool_processor_response (dict): The response from the tool processor.
            result (str): The recognized text.
            conversation (list): The conversation array.
            tool_response_message (Message): The tool response message from OpenAI.
        """
        if tool_processor_response["is_conversational"]:
            conversation.append(tool_response_message)
            tool_call_response_message = self.openai_conversation_builder.create_tool_call_response_message(tool_processor_response)
            conversation.append(tool_call_response_message)
            openai_stream_thread = threading.Thread(target=self.openai_client.stream_response, args=(conversation,))
            openai_stream_thread.start()
        else:
            self.store_conversation(speaker_type=CONVERSATIONS_CONFIG["user"], response=result)

    def continue_conversation(self, result, conversation):
        """
        Continues the conversation with OpenAI based on the given result.

        Args:
            result (str): The recognized text to continue the conversation with.
            conversation (list): The existing conversation array.
        """
        self.openai_client.stop_processing_request()
        conversation = self.openai_conversation_builder.create_recent_conversation_messages_array(result)
        openai_stream_thread = threading.Thread(target=self.openai_client.stream_response, args=(conversation,))
        openai_stream_thread.start()
        logging.info("ROBOT ACTION: Committing user input to memory.")
        self.store_conversation(speaker_type=CONVERSATIONS_CONFIG["user"], response=result)


    def handle_partial_results(self, rec):
        """
        Handles partial results from speech recognition.

        Args:
            rec (KaldiRecognizer): The Vosk recognizer instance.
        """
        partial_result_json = json.loads(rec.PartialResult())
        if 'partial' in partial_result_json and contains_quiet_please_phrase(partial_result_json['partial']):
            self.stop_conversation_and_audio()

    def stop_conversation_and_audio(self):
        """
        Stops the conversation and any ongoing audio processing.
        """
        logging.info("ROBOT THOUGHT: Request to stop talking recognized. Stopping stream.")
        self.stop_all_audio()
        if self.full_assistant_response:
            logging.info("ROBOT ACTION: Committing my partial response to memory")
            self.store_full_assistant_response()

    def stop_all_audio(self):
        self.audio_out_response_buffer = ''
        self.openai_client.stop_processing_request()
        self.audio_out.stop_all_audio()

    def write_to_dump_file(self, data):
        """
        Writes audio data to the dump file if it's open.

        Args:
            data: The audio data to be written to the file.
        """
        if self.dump_filename is not None:
            self.dump_filename.write(data)

    def process_openai_response(self):
        """
        Processes responses from OpenAI's GPT model.

        Retrieves and handles the responses generated by OpenAI.
        """
        while not self.openai_client.response_queue.empty():
            chunk = self.openai_client.response_queue.get()
            if chunk.choices[0].delta.content is not None:
                response_text = chunk.choices[0].delta.content
                print(response_text, end='', flush=True)
                self.update_response_end_time()
                self.audio_out_response_buffer += response_text
                if self.audio_out_response_buffer.endswith(('.', '?', '!', ';')):
                    self.audio_out.add_to_queue(self.audio_out_response_buffer)
                    self.audio_out_response_buffer = ""
                self.full_assistant_response += response_text

        if self.full_assistant_response and self.openai_client.streaming_complete:
            logging.info("ROBOT ACTION: Committing my full response to memory")
            self.store_full_assistant_response()

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
