import logging
import json
from config import OPENAI_SETTINGS, CONVERSATIONS_CONFIG
from database.conversations import ConversationMemoryManager

class OpenAIConversationBuilder:
    """
    A class to build conversation arrays formatted for OpenAI API interactions.
    """

    def __init__(self):
        """
        Initializes the OpenAIConversationBuilder with a ConversationMemoryManager instance.
        """
        self.conversation_memory_manager = ConversationMemoryManager()

    def create_recent_conversation_messages_array(self, latest_conversation_part, overwrite_context_buffer=False, context_buffer=None, image_url=None):
        """
        Creates an array of recent conversations formatted for the OpenAI API.

        Returns:
            List[dict]: A list of message dictionaries with 'role' and 'content' keys, formatted for OpenAI API.
        """
        # Retrieve recent conversations
        context_limit = context_buffer if overwrite_context_buffer else OPENAI_SETTINGS.get('max_context_tokens', 16000)
        recent_conversations = self.conversation_memory_manager.list_recent_conversations(context_limit)

        # Format conversations for OpenAI API
        messages = []
        if OPENAI_SETTINGS.get('initial_system_message'):
            messages.append({'role': 'system', 'content': OPENAI_SETTINGS.get('initial_system_message')})
        for conversation in recent_conversations:
            speaker_role = "user" if conversation.speaker_type == CONVERSATIONS_CONFIG.get("user") else "assistant"
            messages.append({
                "role": speaker_role,
                "content": json.dumps(conversation.response)
            })
        
        if image_url is None:
            messages.append({'role': 'user', 'content': json.dumps(latest_conversation_part)})
        else:
            messages.append({
                'role': 'user', 
                'content': [
                    {'type': 'image_url', 'image_url': image_url},
                    {'type': 'text', 'text': json.dumps(latest_conversation_part)}
                ]
            })
        logging.info(f"ROBOT THOUGHT: Recent conversations formatted for OpenAI: {messages}")
        return messages

    def create_check_if_tool_call_messages(self, result):
        """
        Creates a conversation array to check if the latest user input might require a tool function call.

        Args:
            result (str): The latest part of the conversation input by the user.

        Returns:
            List[dict]: A list of message dictionaries formatted for the OpenAI API,
                        including a system message to determine if the conversation requires a tool call.
        """
        messages = self.create_recent_conversation_messages_array(result, overwrite_context_buffer=True, context_buffer=100)
        tool_check_message = "Respond in JSON format and only in JSON format. Do not return extraneous \n characters. Based on the previous messages, if the conversation seems to require a function or tool to be called to provide an answer, then in JSON format, please provide true or false for the following key: is_tool. Like {'is_tool': true} or {'is_tool': false}. This will inform our next calls. Remember, only respond in JSON format."
        messages.append({'role': 'user', 'content': tool_check_message})
        return messages

    def create_tool_call_response_message(self, tool_function_response):
        """
        Formats a response from a tool function call into a message dictionary for the OpenAI conversation array.

        Args:
            tool_function_response (dict): The response from a tool function call.

        Returns:
            dict: A formatted message dictionary representing the tool function call's response.
        """
        response = {
            "tool_call_id": tool_function_response["tool_call_id"],
            "role": "tool",
            "name": tool_function_response["tool_name"],
            "content": tool_function_response["function_result"]
        }
        return response
    
    @staticmethod
    def messages_array_contains_image(messages):
        """
        Checks if any message in the provided array contains an image URL.

        This method iterates through each message in the `messages` array. For each message,
        it examines the 'content' field, which is expected to be a list. It then iterates
        through each item in this 'content' list. If any item is a dictionary with a 'type'
        key set to 'image_url', the method returns True, indicating that at least one message
        contains an image URL. If no such item is found in any of the messages, the method
        returns False.

        Args:
            self: The instance of the class where this method is defined.
            messages (list): An array of message dictionaries, where each message is expected to
                            have a 'content' key that is a list of items.

        Returns:
            bool: True if any of the messages contains an item in its 'content' list with a
                'type' key set to 'image_url', otherwise False.

        Example:
            >>> messages = [{'content': [{'type': 'text', 'text': 'Hello'}, {'type': 'image_url', 'image_url': 'http://example.com/image.jpg'}]}]
            >>> instance.messages_array_contains_image(messages)
            True
        """
        for message in messages:
            # Check if 'content' is a list
            if isinstance(message.get('content'), list):
                # Iterate through elements in the 'content' list
                for item in message['content']:
                    # Check if the item is a dictionary and has 'type' key with 'image_url' value
                    if isinstance(item, dict) and item.get('type') == 'image_url':
                        return True
        # Return False if no such item is found
        return False
