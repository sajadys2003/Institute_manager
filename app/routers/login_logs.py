from inspect import currentframe
from fastapi import Depends, APIRouter
from app.models import LoginLog
from app.schemas import LoginLogResponse
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from datetime import datetime

router = APIRouter(prefix="/login_logs")


# Endpoints of login
# add all Endpoints login
# -------------------------------------------------------------------------------------------------------

@router.get("/", tags=["login_logs"], response_model=list[LoginLogResponse])
async def get_logins(
        user_auth: CurrentUser,
        pagination: PageDep,
        db: Session = Depends(get_session),
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        user_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            from_date <= LoginLog.login_date if from_date else True,
            LoginLog.login_date <= to_date if to_date else True,
            LoginLog.user_id == user_id if user_id else True
                        )
        return db.scalars(select(LoginLog).where(criteria).limit(pagination.limit).offset(pagination.offset))
