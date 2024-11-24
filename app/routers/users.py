from inspect import currentframe
from fastapi import Depends, HTTPException, status
from app.schemas import UserIn, UserResponse, UserUpdate
from app.dependencies import PageDep, get_session
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from app.routers.security import CurrentUser, get_password_hash, authorized

router = APIRouter(prefix="/users")


# Endpoints of users
# add all Endpoints for user
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["users"], response_model=UserResponse)
async def create_user(user_auth: CurrentUser, user: UserIn, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            user_exist = db.scalars(select(
                CurrentUser).where(CurrentUser.phone_number == user.phone_number)).first()
            user_dict = user.model_dump()
            user_dict["record_date"] = datetime.now()
            user_dict["password"] = get_password_hash(user.password)
            user_dict["recorder_id"] = user_auth.id
            if user_exist and not user_exist.is_enabled:
                for key, value in user_dict.items():
                    setattr(user_exist, key, value)
                db.commit()
                return user_exist
            db_user = CurrentUser(**user_dict)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"{e.args}")


@router.get("/", tags=["users"], response_model=list[UserResponse])
async def get_users(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        if search:
            criteria = and_(CurrentUser.is_enabled,
                            or_(CurrentUser.first_name.contains(search),
                                CurrentUser.last_name.contains(search),
                                CurrentUser.father_name.contains(search),
                                CurrentUser.national_code.contains(search),
                                CurrentUser.phone_number.contains(search)))
            return db.scalars(select(CurrentUser).where(criteria).limit(pagination.limit).offset(pagination.page))


@router.get("/{user_id}", tags=["users"], response_model=UserResponse)
async def get_user_by_id(user_auth: CurrentUser, user_id: int, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_user = db.scalars(select(CurrentUser).where(CurrentUser.id == user_id)).first()
        if db_user:
            return db_user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found!")


@router.put("/{user_id}", tags=["users"], response_model=UserResponse)
async def update_user(
        user_auth: CurrentUser,
        user: UserUpdate,
        phone_number: str,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_user = db.scalars(select(CurrentUser).where(CurrentUser.phone_number == phone_number)).first()
            if not db_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found!")
            if db_user.phone_number != user.phone_number:
                db_user_exist = db.scalars(select(
                    CurrentUser).where(CurrentUser.phone_number == user.phone_number)).first()
                if db_user_exist and not db_user_exist.is_enabled:
                    db_user.is_enabled = False
                    db_user = db_user_exist
            user_dict = user.model_dump(exclude_unset=True)
            user_dict["password"] = get_password_hash(user.password)
            user_dict["record_date"] = datetime.now()
            user_dict["recorder_id"] = user_auth.id
            for key, value in user_dict.items():
                setattr(db_user, key, value)
            db.commit()
            return db_user
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{user_id}", tags=["users"])
async def delete_user(user_auth: CurrentUser, user_id: int, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_user = db.scalars(select(CurrentUser).where(
            CurrentUser.id == user_id, CurrentUser.is_enabled)).first()
        if db_user:
            db_user.is_enabled = False
            db.commit()
            return {"massage": f"user with id: {user_id} successfully deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found!")
