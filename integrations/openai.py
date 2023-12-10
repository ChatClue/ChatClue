import queue
import threading
import logging
from config import OPENAI_SETTINGS
from openai import OpenAI, OpenAIError

class OpenAIClient:
    """
    A client class for interacting with OpenAI's GPT model.

    This class handles the creation and streaming of responses from the OpenAI API based on recognized text input.

    Attributes:
        client (OpenAI): The OpenAI client for API interaction.
        response_queue (queue.Queue): Queue to hold responses from OpenAI.
        stop_signal (threading.Event): Signal to control the streaming of responses.
        model (str): The model name for OpenAI API requests.
    """
    def __init__(self):
        """
        Initializes the OpenAI client with settings from the configuration.

        If an API key is provided in OPENAI_SETTINGS, it uses that key.
        Otherwise, it defaults to the API key set in the environment variable.
        """
        api_key = OPENAI_SETTINGS.get('api_key')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = OpenAI()
        self.response_queue = queue.Queue()
        self.stop_signal = threading.Event()
        self.model = OPENAI_SETTINGS.get('model', "gpt-3.5-turbo")

    def create_completion(self, recognized_text):
        """
        Creates a completion request to the OpenAI API based on recognized text.

        Args:
            recognized_text (str): The text recognized from the audio input.

        Returns:
            The response object from the OpenAI API or None if an error occurs.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': recognized_text}],
                temperature=0,
                stream=True
            )
            return response
        except OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logging.error(f"Error while creating completion: {e}")
            return None

    def stream_response(self, recognized_text):
        """
        Streams the response from the OpenAI API to a queue.

        This method fetches the response for the recognized text and puts each response chunk into a queue.

        Args:
            recognized_text (str): The text recognized from the audio input.
        """
        response = self.create_completion(recognized_text)
        if response:
            for chunk in response:
                if self.stop_signal.is_set():
                    break
                self.response_queue.put(chunk)
        else:
            logging.info("No response from OpenAI API or an error occurred.")
