import logging
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

    def create_recent_conversation_messages_array(self, latest_conversation_part):
        """
        Creates an array of recent conversations formatted for the OpenAI API.

        Returns:
            List[dict]: A list of message dictionaries with 'role' and 'content' keys, formatted for OpenAI API.
        """
        # Retrieve recent conversations
        context_limit = OPENAI_SETTINGS.get('max_context_tokens', 16000)
        recent_conversations = self.conversation_memory_manager.list_recent_conversations(context_limit)

        # Format conversations for OpenAI API
        messages = []
        if OPENAI_SETTINGS.get('initial_system_message'):
            messages.append({'role': 'system', 'content': OPENAI_SETTINGS.get('initial_system_message')})
        for conversation in recent_conversations:
            speaker_role = "user" if conversation.speaker_type == CONVERSATIONS_CONFIG.get("user") else "assistant"
            messages.append({
                "role": speaker_role,
                "content": conversation.response
            })
        messages.append({'role': 'user', 'content': latest_conversation_part})
        logging.info(f"ROBOT THOUGHT: Recent conversations formatted for OpenAI: {messages}")
        return messages
