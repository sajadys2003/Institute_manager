from fastapi import Depends, HTTPException
from app.models import RollCall
from app.schemas import RollCallIn, RollCallResponse, RollCallUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, or_
from app.routers.security import CurrentUser
from inspect import currentframe
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


router = APIRouter()


# Endpoints of roll call
# add all Endpoints for roll call
# -------------------------------------------------------------------------------------------------------


@router.post("/roll_call/create", tags=["roll_call"], response_model=RollCallResponse)
async def create_roll_call(user_auth: CurrentUser, roll_call: RollCallIn, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            roll_call_dict = roll_call.dict()
            roll_call_dict["record_date"] = datetime.now()
            roll_call_dict["recorder_id"] = user_auth.id
            db_roll_call = RollCall(**roll_call_dict)
            db.add(db_roll_call)
            db.commit()
            db.refresh(db_roll_call)
            return db_roll_call
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error adding roll call {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding roll call {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/roll_call", tags=["roll_call"], response_model=list[RollCallResponse])
async def get_roll_call(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: int | None = None):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        if search:
            roll_call = db.scalars(select(RollCall).where(or_(
                RollCall.student_id == search, RollCall.presentation_session_id == search)).
                                   limit(pagination.limit).offset(pagination.offset))
            return roll_call
        roll_calls = db.scalars(select(RollCall).limit(pagination.limit).offset(pagination.offset))
        if roll_calls:
            return roll_calls
        raise HTTPException(status_code=404, detail="roll call not found")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/roll_call/{roll_call_id}", tags=["roll_call"], response_model=RollCallResponse)
async def get_roll_call(user_auth: CurrentUser, roll_call_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_roll_call = db.scalars(select(RollCall).where(RollCall.id == roll_call_id)).first()
        if db_roll_call:
            return db_roll_call
        raise HTTPException(status_code=404, detail="roll call not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/roll_call/update/{roll_call_id}", tags=["roll_call"], response_model=RollCallResponse)
async def update_roll_call(
        user_auth: CurrentUser,
        roll_call: RollCallUpdate,
        roll_call_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_roll_call = db.scalars(select(RollCall).where(RollCall.id == roll_call_id)).first()
            if db_roll_call is None:
                raise HTTPException(status_code=404, detail="roll call not found!")
            roll_call_dict = roll_call.model_dump(exclude_unset=True)
            roll_call_dict["record_date"] = datetime.now()
            roll_call_dict["recorder_id"] = user_auth.id
            for key, value in roll_call_dict.items():
                setattr(roll_call, key, value)
            db.commit()
            return db_roll_call
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating roll call {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating roll call {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/roll_call/delete/{roll_call_id}", tags=["roll_call"])
async def delete_roll_call(user_auth: CurrentUser, roll_call_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_roll_call = db.scalars(select(RollCall).where(RollCall.id == roll_call_id)).first()
        if db_roll_call:
            db.delete(db_roll_call)
            db.commit()
            return {"massage": f"roll call with id: {roll_call_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="roll call not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
