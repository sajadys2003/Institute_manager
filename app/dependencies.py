from sqlalchemy import create_engine
from app.models import Base
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends

# url = "postgresql+psycopg2://postgres:theshimmer_313@localhost:5432/test"
url = "postgresql+psycopg2://postgres:13821382@localhost:5432/postgres"
engine = create_engine(url)

Base.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session(engine), Depends(get_session)]


class Pagination:
    def __init__(self, page: int = 1, size: int = 20):
        self.page = page - 1
        self.limit = size
        self.offset = self.page * self.limit


PageDep = Annotated[Pagination, Depends(Pagination)]
