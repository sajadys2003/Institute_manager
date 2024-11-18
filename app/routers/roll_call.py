from fastapi import Depends, HTTPException, APIRouter
from app.models import RollCall
from app.schemas import RollCallIn, RollCallOut, RollCallUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from inspect import currentframe
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


router = APIRouter()


# Endpoints of roll call
# add all Endpoints for roll call
# -------------------------------------------------------------------------------------------------------


@router.post("/roll_call/create", tags=["roll_call"], response_model=RollCallOut)
async def create_roll_call(user_auth: CurrentUser, roll_call: RollCallIn, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
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
            raise HTTPException(status_code=400, detail=f"integrity error adding roll call {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding roll call {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/roll_call", tags=["roll_call"], response_model=list[RollCallOut])
async def get_roll_calls(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session),
        presentation_session_id: int | None = None, student_id: int | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(
            RollCall.presentation_session_id == presentation_session_id
            if (presentation_session_id or presentation_session_id == 0) else True,
            RollCall.student_id == student_id
            if (student_id or student_id == 0) else True
        )
        return db.scalars(select(RollCall).where(criteria).limit(pagination.limit).offset(pagination.offset))
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/roll_call/{roll_call_id}", tags=["roll_call"], response_model=RollCallOut)
async def get_roll_call(user_auth: CurrentUser, roll_call_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_roll_call = db.scalars(select(RollCall).where(RollCall.id == roll_call_id)).first()
        if db_roll_call:
            return db_roll_call
        raise HTTPException(status_code=404, detail="roll call not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/roll_call/update/{roll_call_id}", tags=["roll_call"], response_model=RollCallOut)
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
                setattr(db_roll_call, key, value)
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