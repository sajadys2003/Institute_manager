from app.models import engine
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class Pagination:
    def __init__(self, page: int = 1, size: int = 20):
        self.page = page - 1
        self.limit = size
        self.offset = self.page * self.limit


PageDep = Annotated[Pagination, Depends(Pagination)]


class CommonQueryParams(Pagination):
    def __init__(self, q: str | None = None, page: int = 1, size: int = 20):
        super().__init__(page, size)
        self.q = f"%{q.strip()}%" if q else None


CommonsDep = Annotated[CommonQueryParams, Depends(CommonQueryParams)]
