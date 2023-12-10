import queue
import logging
import json
import threading
import time
import sounddevice as sd
from vosk import KaldiRecognizer
from integrations.openai import OpenAIClient
from utils.audio_helpers import contains_quiet_please_phrase, contains_wake_phrase

class AudioProcessor:
    def __init__(self, model, samplerate, device, blocksize, dump_filename=None):
        self.model = model
        self.samplerate = samplerate
        self.device = device
        self.blocksize = blocksize
        self.dump_filename = dump_filename
        self.audio_queue = queue.Queue()
        self.openai_client = OpenAIClient()
    
        self.last_wake_time = 0
        self.last_response_end_time = 0
    
    def open_dump_file(self):
        if self.dump_filename is not None:
            self.dump_filename = open(self.dump_filename, "wb")
    
    def close_dump_file(self):
        if self.dump_filename is not None:
            self.dump_filename.close()
    
    def should_process(self, result, current_time):
        # Ensures wake words are not necessary for all communication attempts.
        return contains_wake_phrase(result) or (current_time - self.last_wake_time <= 10) or (current_time - self.last_response_end_time <= 10)

    def update_wake_time(self):
        self.last_wake_time = time.time()

    def update_response_end_time(self):
        self.last_response_end_time = time.time()

    def callback(self, indata, frames, time, status):
        if status:
            logging.warning(status)
        self.audio_queue.put(bytes(indata))

    def process_stream(self):
        self.open_dump_file()
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=self.blocksize, device=self.device,
                               dtype="int16", channels=1, callback=self.callback):
            logging.info("#" * 80)
            logging.info("Press Ctrl+C to stop the recording")
            logging.info("#" * 80)

            rec = KaldiRecognizer(self.model, self.samplerate)
            openai_stream_thread = None

            while True:
                current_time = time.time()
                data = self.audio_queue.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())["text"]
                    if result != '':
                        logging.info("ROBOT HEARD: " + result)
                        if self.should_process(result, current_time):
                            if not openai_stream_thread or not openai_stream_thread.is_alive():
                                self.update_wake_time()
                                self.openai_client.stop_signal.clear()
                                openai_stream_thread = threading.Thread(target=self.openai_client.stream_response, args=(result,))
                                openai_stream_thread.start()
                        else:
                            logging.info("ROBOT THOUGHT: Ignoring Conversation, it doesn't appear to be relevant.")

                partial_result_json = json.loads(rec.PartialResult())
                if 'partial' in partial_result_json and contains_quiet_please_phrase(partial_result_json['partial']):
                    logging.info("ROBOT THOUGHT: Request to stop talking recognized. Stopping OpenAI Stream.")
                    self.openai_client.stop_signal.set()
                    with self.openai_client.response_queue.mutex:
                        self.openai_client.response_queue.queue.clear()

                if self.dump_filename is not None:
                    self.dump_filename.write(data)

                while not self.openai_client.response_queue.empty():
                    chunk = self.openai_client.response_queue.get()
                    if chunk.choices[0].delta.content is not None:
                        print(chunk.choices[0].delta.content, end='')
                        self.update_response_end_time()
        
        self.close_dump_file()