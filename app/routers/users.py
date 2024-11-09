from fastapi import Depends, HTTPException
from app.models import User
from app.schemas import UserIn, UserResponse, UserUpdate
from app.dependencies import get_session, CommonsDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_, or_
from app.routers.authentication import AuthorizedUser, get_password_hash

router = APIRouter()


# Endpoints of users
# add all Endpoints for user
# -------------------------------------------------------------------------------------------------------


@router.post("/users/create", tags=["users"], response_model=UserResponse)
async def create_user(user: UserIn, db: Session = Depends(get_session)):
    user_dict = user.dict()
    user_dict["record_date"] = datetime.now()
    user_dict["hashed_password"] = get_password_hash(user.password)
    db_user = User(**user_dict)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/users", tags=["users"], response_model=list[UserResponse])
async def get_users(user_auth: AuthorizedUser, db: Session = Depends(get_session), params=CommonsDep):
    if user_auth:

        if params.q:
            criteria = and_(User.is_enabled,
                            or_(User.first_name.contains(params.q),
                                User.last_name.contains(params.q),
                                User.father_name.contains(params.q),
                                User.national_code.contains(params.q),
                                User.phone_number.contains(params.q)))

            return db.scalars(select(User).where(criteria).limit(params.size).offset(params.page))

        return db.scalars(select(User).limit(params.size).offset(params.page))


@router.get("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def get_user(user_auth: AuthorizedUser, user_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_user = db.scalars(select(User).where(User.id == user_id)).first()
        if db_user:
            return db_user
        raise HTTPException(status_code=404, detail="user not found!")


@router.put("/users/update/{user_id}", tags=["users"], response_model=UserResponse)
async def update_user(user_auth: AuthorizedUser, user: UserUpdate, user_id: int, db: Session = Depends(get_session)):
    if user_auth:

        db_user = db.scalars(select(User).where(User.id == user_id)).first()

        if db_user is None:
            raise HTTPException(status_code=404, detail="user not found!")

        user_dict = user.model_dump(exclude_unset=True)
        user_dict["record_date"] = datetime.now()
        user_dict["recorder_id"] = user_auth.id

        for key, value in user:
            setattr(db_user, key, value)

        db.commit()

        return db_user


@router.delete("/users/delete/{user_id}", tags=["users"])
async def delete_user(user_auth: AuthorizedUser, user_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_user = db.scalars(select(User).where(User.id == user_id)).first()
        if db_user:
            db_user.is_enabled = False
            db.commit()
            return {"massage": f"user with id: {user_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="user not found!")
