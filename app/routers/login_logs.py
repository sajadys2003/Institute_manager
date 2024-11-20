from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter
from app.models import Login
from app.schemas import LoginOut
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from datetime import datetime

router = APIRouter()


# Endpoints of login
# add all Endpoints login
# -------------------------------------------------------------------------------------------------------

@router.get("/login_log", tags=["login_log"], response_model=list[LoginOut])
async def get_logins(user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session),
                     from_date: datetime | None = None, to_date: datetime | None = None):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(from_date <= Login.login_date if from_date else True,
                        Login.login_date <= to_date if to_date else True
                        )
        db_login = db.scalars(select(Login).where(criteria).limit(pagination.limit).offset(pagination.offset))
        if db_login:
            return db_login
        raise HTTPException(status_code=404, detail="login not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/login_log/{user_id}", tags=["login_log"], response_model=list[LoginOut])
async def get_logins_by_id(
        user_auth: CurrentUser, pagination: PageDep, user_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_login = db.scalars(
            select(Login).where(Login.user_id == user_id).limit(pagination.limit).offset(pagination.offset))
        if db_login:
            return db_login
        raise HTTPException(status_code=404, detail="login not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
