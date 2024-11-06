from sqlalchemy import create_engine
from app.models import Base
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends

# url = "postgresql+psycopg2://postgres:theshimmer_313@localhost:5432/test"
url = "sqlite:////home/plus/PycharmProjects/Radman/app/test.db"
engine = create_engine(url)

Base.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class CommonQueryParams:
    def __init__(self, q: str | None = None, page: int = 1, size: int = 20):
        self.q = q.strip() if q else None
        self.page = page - 1
        self.limit = size
        self.offset = self.page * self.limit



CommonsDep = Annotated[CommonQueryParams, Depends(CommonQueryParams)]

