# database/models.py

from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func

# Base class for declarative class definitions
Base = declarative_base()

class Conversation(Base):
    """
    Represents the 'conversations' table in the database.

    This class defines the schema for storing conversation data, including
    user prompts and assistant responses along with their respective embeddings.
    """

    # Name of the table in the database
    __tablename__ = 'conversations'

    # Columns of the table
    id = Column(Integer, primary_key=True, 
                doc="The unique identifier for each conversation.")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        doc="Timestamp when the conversation was created.")
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                        doc="Timestamp when the conversation was last updated.")
    
    speaker_type = Column(Integer, nullable=False,
                        doc="The type of speaker (user or assistant).", index=True)
    
    speaker_metadata = Column(Text, nullable=True,
                        doc="The metadata of the speaker.") # Future planning for speaker diarization.
    
    response = Column(Text, nullable=False, 
                        doc="The text of the user's prompt in the conversation.")
    
    response_tokens = Column(Integer, nullable=False, 
                    doc="The count of tokens in the users's prompt.")
                                     
    response_embedding = Column(Vector(1536), nullable=False,
                                 doc="The vector embedding of the user's prompt, "
                                     "representing linguistic features.")

class SystemState(Base):
    """
    Represents the 'system_state' table in the database.

    This class defines the schema for storing system state data, including
    the current state of the system and the corresponding embeddings.
    """

    # Name of the table in the database
    __tablename__ = 'system_state'

    # Columns of the table
    id = Column(Integer, primary_key=True, 
                doc="The unique identifier for each system state.")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        doc="Timestamp when the system state was created.")
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                        doc="Timestamp when the system state was last updated.")
    
    last_wake_time = Column(Integer, nullable=True, 
                        doc="The last time a request was received from the user.")