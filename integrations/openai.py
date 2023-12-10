import queue
import threading
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()
        self.response_queue = queue.Queue()
        self.stop_signal = threading.Event()

    def create_completion(self, recognized_text):
        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': recognized_text}],
            temperature=0,
            stream=True
        )
        return response

    def stream_response(self, recognized_text):
        response = self.create_completion(recognized_text)
        for chunk in response:
            if self.stop_signal.is_set():
                break
            self.response_queue.put(chunk)
