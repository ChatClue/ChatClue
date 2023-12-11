import logging
from sqlalchemy import create_engine
from config import DATABASE_CONFIG

def get_engine():
    """
    Creates and returns a SQLAlchemy engine.

    This engine is the entry point to the SQLAlchemy library, providing a connection
    to the specified PostgreSQL database using configuration parameters defined in
    DATABASE_CONFIG. It uses the psycopg driver for PostgreSQL.

    The engine's connection string is dynamically constructed based on
    the presence of a password in the DATABASE_CONFIG.

    Returns:
        A SQLAlchemy engine object connected to the PostgreSQL database.
    """

    # Check if 'password' key exists and is not an empty string
    if DATABASE_CONFIG.get('password'):
        logging.info("Connecting to database with password...")
        # Include the password in the connection string
        db_url = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@" \
                 f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"
    else:
        logging.info("Connecting to database without password...")
        # Omit the password from the connection string
        db_url = f"postgresql://{DATABASE_CONFIG['user']}@" \
                 f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"

    # Create and return the SQLAlchemy engine
    return create_engine(db_url)