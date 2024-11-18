from app.models import User
from app.schemas import UserIn, UserUpdate, UserResponse
from .security import get_password_hash


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users")


async def get_by_id(db: SessionDep, user_id: int) -> User:
    criteria = and_(
        User.id == user_id,
        User.is_enabled
    )
    stored_record = db.query(User).where(criteria).scalar()
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[UserResponse])
async def get_users(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = and_(
                User.is_enabled,
                or_(
                    User.first_name.contains(q),
                    User.last_name.contains(q),
                    User.father_name.contains(q),
                    User.phone_number.contains(q),
                    User.national_code.contains(q)
                )
            )
        else:
            criteria = User.is_enabled

        stored_records = db.query(User).where(criteria)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{user_id}", response_model=UserResponse)
async def get_user_by_id(
        db: SessionDep,
        user_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, user_id)
        return stored_record


@router.post(path="/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        db: SessionDep,
        data: UserIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        data_dict = data.model_dump()
        data_dict.update(
            {
                "password": get_password_hash(data.password),
                "recorder_id": current_user.id,
                "record_date": datetime.now()
            }
        )
        criteria = User.phone_number == data.phone_number
        existing_user = db.query(User).where(criteria).scalar()
        if existing_user:
            if existing_user.is_enabled:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
            else:
                existing_user.is_enabled = True
                try:
                    for key, value in data_dict.items():
                        setattr(existing_user, key, value)
                    db.commit()
                    return existing_user
                except IntegrityError as e:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
        else:
            try:
                new_record = User(**data_dict)
                db.add(new_record)
                db.commit()
                return new_record
            except IntegrityError as e:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")

@router.put(path="/{phone_number}", response_model=UserResponse)
async def update_user(
        db: SessionDep,
        phone_number: str,
        data: UserUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        criteria = and_(
            User.phone_number == phone_number,
            User.is_enabled
            )
        to_update = db.query(User).where(criteria).scalar()
        if not to_update:
            raise HTTPException(status_code=404, detail="Not found")

        if password := data.password:
            data.password = get_password_hash(password)

        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})

        if data.phone_number:
            criteria = and_(
                User.phone_number == data.phone_number,
                User.phone_number != to_update.phone_number
            )
            existing_user = db.query(User).where(criteria).scalar()
            if existing_user:
                if existing_user.is_enabled:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
                else:
                    to_update.is_enabled = False
                    existing_user.is_enabled = True
                    to_update = existing_user

        try:
            for key, value in data_dict.items():
                setattr(to_update, key, value)
            db.commit()
            return to_update
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        db: SessionDep,
        user_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, user_id)
        stored_record.is_enabled = False
        db.commit()
