from .connection import get_engine
from .models import Base
from sqlalchemy import text

class DatabaseSetup:
    """
    This class is responsible for database setup tasks, particularly
    for ensuring that all defined tables in SQLAlchemy models are created in the database.
    """

    @staticmethod
    def initial_setup():
        """
        Creates tables in the database based on the SQLAlchemy models.

        This method uses the SQLAlchemy engine to connect to the database and creates
        any tables that haven't been created yet as defined in the SQLAlchemy model classes.
        It's intended to be run during the initial setup phase of the application.
        """

        # Obtain the SQLAlchemy engine
        engine = get_engine()

        # Ensure vector extension is enabled.
        with engine.begin() as connection:
            # Create extension 'pgvector' if it is not created yet
            # Remember, you may need to install pgvector on your system before this will work properly.
            # https://github.com/pgvector/pgvector.git for instructions.
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Create all tables in the database defined in the SQLAlchemy models
        # This will have no effect on existing tables that match the model definitions
        Base.metadata.create_all(engine)
