from fastapi import Depends, HTTPException, APIRouter, status
from app.models import RollCall
from app.schemas import RollCallIn, RollCallResponse, RollCallUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from inspect import currentframe
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/roll_calls")


# Endpoints of roll call
# add all Endpoints for roll call
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["roll_calls"], response_model=RollCallResponse)
async def create_roll_call(user_auth: CurrentUser, roll_call: RollCallIn, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            roll_call_dict = roll_call.model_dump()
            roll_call_dict["record_date"] = datetime.now()
            roll_call_dict["recorder_id"] = user_auth.id
            db_roll_call = RollCall(**roll_call_dict)
            db.add(db_roll_call)
            db.commit()
            db.refresh(db_roll_call)
            return db_roll_call
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["roll_calls"], response_model=list[RollCallResponse])
async def get_roll_calls(
        user_auth: CurrentUser,
        pagination: PageDep,
        db: Session = Depends(get_session),
        presentation_session_id: int | None = None,
        student_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            RollCall.presentation_session_id == presentation_session_id
            if (presentation_session_id or presentation_session_id == 0) else True,
            RollCall.student_id == student_id
            if (student_id or student_id == 0) else True
        )
        return db.scalars(select(RollCall).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.put("/", tags=["roll_calls"], response_model=RollCallResponse)
async def update_roll_call(
        user_auth: CurrentUser,
        roll_call: RollCallUpdate,
        student_id: int,
        presentation_session_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_roll_call = db.scalars(
                select(RollCall).where(and_(RollCall.student_id == student_id,
                                            RollCall.presentation_session_id == presentation_session_id))).first()
            if db_roll_call is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="roll call not found!")
            roll_call_dict = roll_call.model_dump(exclude_unset=True)
            roll_call_dict["record_date"] = datetime.now()
            roll_call_dict["recorder_id"] = user_auth.id
            for key, value in roll_call_dict.items():
                setattr(db_roll_call, key, value)
            db.commit()
            return db_roll_call
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"{e.args}")


@router.delete("/", tags=["roll_calls"])
async def delete_roll_call(
        user_auth: CurrentUser,
        student_id: int,
        presentation_session_id,
        db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_roll_call = db.scalars(
                select(RollCall).where(and_(RollCall.student_id == student_id,
                                            RollCall.presentation_session_id == presentation_session_id))).first()
        if db_roll_call:
            db.delete(db_roll_call)
            db.commit()
            return {"massage": "roll call successfully deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="roll call not found!")
