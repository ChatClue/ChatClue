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

    def create_recent_conversation_messages_array(self, latest_conversation_part, overwrite_context_buffer=False, context_buffer=None):
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
        messages.append({'role': 'user', 'content': json.dumps(latest_conversation_part)})
        logging.info(f"ROBOT THOUGHT: Recent conversations formatted for OpenAI: {messages}")
        return messages

    def create_check_if_tool_call_messages(self,result):
        messages = self.create_recent_conversation_messages_array(result, overwrite_context_buffer=True, context_buffer=500)
        messages.append({'role': 'system', 'content': 'Based on the previous messages, if the conversation seems to require a function or tool to be called to provide an answer, then in JSON format, please provide true or false for the following key: is_tool. This will inform our next calls'})
        return messages