from celery import shared_task
from database.conversations import ConversationMemoryManager
from database.system_state import SystemStateManager
from datetime import datetime

@shared_task
def store_conversation_task(speaker_type, response):
    """
    A Celery task for storing conversation parts in the database.

    This asynchronous task takes a speaker type and a response, and stores them in the database
    using the ConversationMemoryManager. It is designed to offload the database writing process
    from the main execution thread, improving performance and responsiveness.

    Args:
        speaker_type (str): The type of speaker (e.g., 'user' or 'assistant'), indicating who is speaking.
        response (str): The text of the response or conversation part to be stored.
    """
    # Initialize the conversation memory manager
    manager = ConversationMemoryManager()
    # Add the conversation part to the database
    manager.add_conversation(speaker_type=speaker_type, response=response)

@shared_task
def update_system_state_task(last_wake_time):
    """
    A Celery task for updating the system state in the database.

    This asynchronous task updates the system state, such as the last wake time of the system.
    It offloads the database update process from the main execution thread.
    """
    # Initialize the system state manager
    state_manager = SystemStateManager()

    # Update the last wake time in the database
    state_manager.update_system_state(last_wake_time=last_wake_time)