from celery import shared_task
from database.conversations import ConversationMemoryManager

@shared_task
def store_conversation_task(speaker_type, response):
    manager = ConversationMemoryManager()
    manager.add_conversation(speaker_type=speaker_type, response=response)
