from sys import prefix

from app.models import User
from app.schemas import UserIn
from app.schemas import UserUpdate
from app.schemas import UserResponse

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.dependencies import get_db
from typing import Annotated
from datetime import datetime
from fastapi_pagination import Page, paginate

router = APIRouter(prefix="/users")


def create_new_record(data: UserIn, db: Session, force: bool):
    criteria = User.national_code == data.national_code.strip()
    stored_record = db.query(User).where(criteria).scalar()
    if stored_record:
        if force:
            pass
        else:

            raise HTTPException(status_code=400,
                                detail="a user with duplicate national_code found "

                                       "set force=True to update user")


@router.get(path="", response_model=list[UserResponse])
async def get_all(
        db: Annotated[Session, Depends(get_db)],
        page: int = 1,
        size: int = 20,
        search_query: str | None = None,
):
    if search_query := search_query.strip():
        criteria = and_(
            User.is_enabled.is_(True),
            or_(User.first_name.contains(search_query),
                User.last_name.contains(search_query),
                User.father_name.contains(search_query),
                User.national_code.contains(search_query),
                User.phone_number.contains(search_query)),
        )
    else:
        criteria = User.is_enabled.is_(True)
    page -= 1
    stored_records = db.query(User).where(criteria).offset(size * page).limit(size)
    return stored_records.all()


@router.get(path="/{user_id}", response_model=UserResponse)
async def get_one(
        db: Annotated[Session, Depends(get_db)],
        user_id: int
):
    stored_record = db.get(User, user_id)

    if stored_record.is_enabled:
        return stored_record
    else:
        raise HTTPException(status_code=400, detail="Disabled record")

# @router.post(path="/", response_model=UserResponse, status_code=201)
# async def create(
#         db: Annotated[Session, Depends(get_session)],
#         data: UserIn,
#         force: bool = False
# ):
#     if stored_record:
#         if force:  # update
#             stored_record.record_date = datetime.now()
#             db.commit()
#             return stored_record
#         else:
#             raise HTTPException(status_code=409, detail="Duplicate name, set force=True to update record")
#     else:  # add
#         data.record_date = datetime.now()
#         new_record = Role(**data.model_dump())
#         db.add(new_record)
#         db.commit()
#         return new_record
