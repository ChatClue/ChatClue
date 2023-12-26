from sqlalchemy.orm import sessionmaker
from .models import SystemState, Base
from .connection import get_engine

class SystemStateManager:
    """
    Manages database operations for the SystemState table,
    including insertions and updates.
    """

    def __init__(self):
        """
        Initializes the SystemStateManager with a database session.
        """
        self.engine = get_engine()

    def get_or_create_state(self):
        """
        Retrieves the current system state from the database, or creates it if it doesn't exist.
        """
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            state = session.query(SystemState).first()
            if not state:
                state = SystemState()
                session.add(state)
                session.commit()
            return state

    def update_system_state(self, **updates):
        """
        Updates the system state in the database.

        Parameters:
            **updates: Arbitrary keyword arguments representing the fields to update and their new values.

        Example:
            To update the last wake time of the system state:
            
            update_system_state(last_wake_time=datetime.now())
        """
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            state = session.query(SystemState).first()
            if not state:
                state = SystemState()
                session.add(state)

            for key, value in updates.items():
                setattr(state, key, value)

            session.commit()
