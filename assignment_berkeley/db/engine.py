from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from assignment_berkeley.db.models import Base

engine: Engine = None
DBSession = sessionmaker()


def init_db(file: str):
    """Initialize the database, create engine and session."""
    engine = create_engine(file)
    Base.metadata.bind = engine
    DBSession.configure(bind=engine)
