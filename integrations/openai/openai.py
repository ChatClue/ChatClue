import queue
import threading
import logging
import tiktoken
import time
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
        self.model = OPENAI_SETTINGS.get('model', "gpt-3.5-turbo-1106")
        self.embedding_model = OPENAI_SETTINGS.get('embedding_model', "text-embedding-ada-002")
        self.temperature = OPENAI_SETTINGS.get('temperature', 0.5)
        self.streaming_complete = False

    def create_completion(self, recent_messages, streaming=True, response_format=None, tools=None, is_tool_call=False):
        """
        Creates a completion request to the OpenAI API based on recognized text.

        Args:
            recognized_text (str): The text recognized from the audio input.

        Returns:
            The response object from the OpenAI API or None if an error occurs.
        """
        try:
            tool_choice = None
            if tools is not None and not is_tool_call:
                recent_messages[-1]["content"] = "Please pick a tool from the tools array and return a tools response to complete this request: " + recent_messages[-1]["content"]
                tool_choice = "auto"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=recent_messages,
                tools=tools,
                temperature=self.temperature,
                stream=streaming,
                response_format=response_format,
                tool_choice=tool_choice
            )
            return response
        except OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logging.error(f"Error while creating completion: {e}")
            return None

    def stream_response(self, conversation):
        """
        Streams the response from the OpenAI API to a queue.

        This method fetches the response for the recognized text and puts each response chunk into a queue.
        The method frequently checks for a stop signal to terminate streaming immediately.

        Args:
            recognized_text (str): The text recognized from the audio input.
        """
        self.streaming_complete = False
        try:
            response = self.create_completion(conversation)
            if response:
                for chunk in response:
                    if self.stop_signal.is_set():
                        logging.info("Streaming stopped due to stop signal.")
                        break
                    self.response_queue.put(chunk)
            else:
                logging.info("No response from OpenAI API or an error occurred.")
        except Exception as e:
            logging.error(f"Error during streaming: {e}")
        finally:
            self.streaming_complete = True

    def create_embeddings(self, text):
        """
        Generates embeddings for the given text using the OpenAI API.

        Args:
            text (str): The text to generate embeddings for.

        Returns:
            The embedding vector as a list, or None if an error occurs.
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            # return response.
            return response.data[0].embedding
        except OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logging.error(f"Error while creating embeddings: {e}")
            return None
    
    def calculate_token_count(self, text):
        """
        Calculates the number of tokens for the given text using OpenAI's GPT model.

        Args:
            text (str): The text to calculate the token count for.

        Returns:
            int: The number of tokens in the text.
        """
        enc = tiktoken.encoding_for_model(self.model)
        return len(enc.encode(text))
    
    def stop_processing_request(self):
        """
        Stops processing the current request immediately and clears the response queue.
        """
        self.stop_signal.set()  # Signal to stop streaming
        self.full_stop()
        time.sleep(0.5)
        self.full_stop()
        self.stop_signal.clear()  # Reset the stop signal for future requests

    
    def clear_queue(self):
        """
        Clears all items from the response queue.
        """
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()  # Remove all items from the queue
                self.response_queue.task_done()
            except queue.Empty:
                break
    
    def full_stop(self):
        self.clear_queue()      # Clear the queue immediately
        self.streaming_complete = False  # Reset the streaming state
    
    def shutdown(self):
        self.stop_processing_request()