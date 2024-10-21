from sqlalchemy import create_engine
from src.models import Base
from sqlalchemy.orm import Session

"""
initialize database and define a function to get 'session' from. 
This 'session' later on will be used to do all the crud operations.
"""

url = "postgresql+psycopg2://postgres:theshimmer_313@localhost:5432/test"
engine = create_engine(url)

Base.metadata.create_all(bind=engine)  # create all tables stored in metadata


def get_session():
    with Session(engine) as session:
        yield session
