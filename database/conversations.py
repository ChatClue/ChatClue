from sqlalchemy.orm import sessionmaker
from .models import Conversation, Base
from .connection import get_engine
from integrations.openai import OpenAIClient

class ConversationMemoryManager:
    """
    Manages database operations for the Conversation table,
    including insertions, updates, deletions, and queries.
    """

    def __init__(self):
        """
        Initializes the ConversationManager with a database session.
        """
        self.engine = get_engine()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_conversation(self, speakerType, response):
        """
        Adds a new conversation to the database, automatically creating embeddings and calculating token counts.

        Parameters:
            user_prompt (str): The user's prompt text.
            assistant_response (str): The assistant's response text.
        """
        openai_client = OpenAIClient()

        # Generate embeddings
        response_embedding = openai_client.create_embeddings(response)

        # Calculate token counts
        response_tokens = openai_client.calculate_token_count(response)

        new_conversation = Conversation(
            speakerType=speakerType,
            response=response,
            responseTokens=response_tokens,
            responseEmbedding=response_embedding,
        )

        self.session.add(new_conversation)
        self.session.commit()

    def get_conversation(self, conversation_id):
        """
        Retrieves a conversation from the database by its ID.
        """
        return self.session.query(Conversation).filter_by(id=conversation_id).first()

    def update_conversation(self, conversation_id, **updates):
        """
        Updates a conversation in the database based on the provided conversation ID and update fields.

        Parameters:
            conversation_id (int): The ID of the conversation to be updated.
            **updates: Arbitrary keyword arguments representing the fields to update and their new values.

        Example:
            To update the user prompt and tokens of a conversation with ID 123:
            
            update_conversation(123, userPrompt="New prompt text", userPromptTokens=5)

        Note:
            The fields in **updates should match the column names of the Conversation model.
        """
        self.session.query(Conversation).filter_by(id=conversation_id).update(updates)
        self.session.commit()

    def delete_conversation(self, conversation_id):
        """
        Deletes a conversation from the database.
        """
        conversation = self.session.query(Conversation).filter_by(id=conversation_id).first()
        if conversation:
            self.session.delete(conversation)
            self.session.commit()

    def list_conversations(self, after_date=None, before_date=None):
        """
        Lists all conversations in the database within a specified date range.

        Parameters:
            after_date (datetime): Optional. Retrieve conversations after this date.
            before_date (datetime): Optional. Retrieve conversations before this date.

        Returns:
            List of Conversation objects that match the criteria.
        """
        query = self.session.query(Conversation)
        
        if after_date:
            query = query.filter(Conversation.createdAt >= after_date)
        
        if before_date:
            query = query.filter(Conversation.createdAt <= before_date)

        return query.all()

    def close_session(self):
        """
        Closes the database session.
        """
        self.session.close()
