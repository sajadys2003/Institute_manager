from inspect import currentframe
from fastapi import Depends, HTTPException
from app.models import Login
from app.schemas import LoginResponse
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from fastapi import APIRouter
from sqlalchemy import select
from app.routers.security import CurrentUser

router = APIRouter()


# Endpoints of login
# add all Endpoints login
# -------------------------------------------------------------------------------------------------------

@router.get("/login_log", tags=["login_log"], response_model=list[LoginResponse])
async def get_login(user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_login = db.scalars(select(Login).limit(pagination.limit).offset(pagination.offset))
        if db_login:
            return db_login
        raise HTTPException(status_code=404, detail="login not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/login_log/{user_id}", tags=["login_log"], response_model=LoginResponse)
async def get_financial_category(
        user_auth: CurrentUser, pagination: PageDep, user_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_login = db.scalars(
            select(Login).where(Login.user_id == user_id).limit(pagination.limit).offset(pagination.offset))
        if db_login:
            return db_login
        raise HTTPException(status_code=404, detail="login not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
