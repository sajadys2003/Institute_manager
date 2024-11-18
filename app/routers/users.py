from inspect import currentframe
from fastapi import Depends, HTTPException
from app.models import User
from app.schemas import UserIn, UserResponse, UserUpdate
from app.dependencies import PageDep, get_session
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.routers.security import CurrentUser, get_password_hash

router = APIRouter()


# Endpoints of users
# add all Endpoints for user
# -------------------------------------------------------------------------------------------------------


@router.post("/users/create", tags=["users"], response_model=UserResponse)
async def create_user(user_auth: CurrentUser, user: UserIn, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            user_exist = db.scalars(select(User).where(or_(User.phone_number == user.phone_number))).first()
            user_dict = user.model_dump()
            user_dict["record_date"] = datetime.now()
            user_dict["password"] = get_password_hash(user.password)
            user_dict["recorder_id"] = user_auth.id
            if user_exist and not user_exist.is_enabled:
                for key, value in user_dict.items():
                    setattr(user_exist, key, value)
                db.commit()
                return user_exist
            db_user = User(**user_dict)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error adding user {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding user {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/users", tags=["users"], response_model=list[UserResponse])
async def get_users(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        if search:
            criteria = and_(User.is_enabled,
                            or_(User.first_name.contains(search),
                                User.last_name.contains(search),
                                User.father_name.contains(search),
                                User.national_code.contains(search),
                                User.phone_number.contains(search)))
            users = db.scalars(select(User).where(criteria).limit(pagination.limit).offset(pagination.page))
            if users:
                return users
            raise HTTPException(status_code=404, detail="user not found!")
        users = db.scalars(select(User).where(User.is_enabled).limit(pagination.limit).offset(pagination.offset))
        if users:
            return users
        raise HTTPException(status_code=404, detail="user not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def get_user(user_auth: CurrentUser, user_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_user = db.scalars(select(User).where(User.id == user_id)).first()
        if db_user:
            return db_user
        raise HTTPException(status_code=404, detail="user not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/users/update/{user_id}", tags=["users"], response_model=UserResponse)
async def update_user(user_auth: CurrentUser, user: UserUpdate, phone_number: str, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_user = db.scalars(select(User).where(User.phone_number == phone_number)).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="user not found!")
            if db_user.phone_number != user.phone_number:
                db_user_exist = db.scalars(select(User).where(User.phone_number == user.phone_number)).first()
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
            raise HTTPException(status_code=400, detail=f"integrity error updating user {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating user {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/users/delete/{user_id}", tags=["users"])
async def delete_user(user_auth: CurrentUser, user_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_user = db.scalars(select(User).where(User.id == user_id, User.is_enabled)).first()
        if db_user:
            db_user.is_enabled = False
            db.commit()
            return {"massage": f"user with id: {user_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="user not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
