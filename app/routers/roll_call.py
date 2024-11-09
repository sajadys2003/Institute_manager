from fastapi import Depends, HTTPException
from app.models import RollCall
from app.schemas import RollCall, RollCallResponse, RollCallUpdate
from app.dependencies import get_session, CommonsDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_, or_
from app.routers.authentication import AuthorizedUser

router = APIRouter()


# Endpoints of roll call
# add all Endpoints for roll call
# -------------------------------------------------------------------------------------------------------


@router.post("/roll_call/create", tags=["roll_call"], response_model=RollCallResponse)
async def create_roll_call(user_auth: AuthorizedUser, roll_call: RollCall, db: Session = Depends(get_session)):

    if user_auth:
        roll_call_dict = roll_call.dict()
        roll_call_dict["record_date"] = datetime.now()
        roll_call_dict["recorder_id"] = user_auth.id
        db_roll_call = RollCall(**roll_call_dict)
        db.add(db_roll_call)
        db.commit()
        db.refresh(db_roll_call)

        return db_roll_call


@router.get("/roll_call", tags=["roll_call"], response_model=list[RollCallResponse])
async def get_roll_call(user_auth: AuthorizedUser, db: Session = Depends(get_session), params=CommonsDep):
    if user_auth:

        if params.q:
            criteria = and_(RollCall.is_enabled,
                            or_(RollCall.name.contains(params.q),
                                RollCall.presentation_session_id.contains(int(params.q)),
                                RollCall.student_id.contains(int(params.q))))

            return db.scalars(select(RollCall).where(criteria).limit(params.size).offset(params.page))

        return db.scalars(select(RollCall).limit(params.size).offset(params.page))


@router.get("/roll_call/{roll_call_id}", tags=["roll_call"], response_model=RollCallResponse)
async def get_roll_call(user_auth: AuthorizedUser, roll_call_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_roll_call = db.scalars(select(RollCall).where(RollCall.id == roll_call_id)).first()
        if db_roll_call:
            return db_roll_call
        raise HTTPException(status_code=404, detail="roll call not found!")


@router.put("/roll_call/update/{roll_call_id}", tags=["roll_call"], response_model=RollCallResponse)
async def update_course_price(
        user_auth: AuthorizedUser,
        roll_call: RollCallUpdate,
        roll_call_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:

        db_roll_call = db.scalars(select(RollCall).where(RollCall.id == roll_call_id)).first()

        if db_roll_call is None:
            raise HTTPException(status_code=404, detail="roll call not found!")

        roll_call_dict = roll_call.model_dump(exclude_unset=True)
        roll_call_dict["record_date"] = datetime.now()
        roll_call_dict["recorder_id"] = user_auth.id

        for key, value in roll_call:
            setattr(roll_call, key, value)

        db.commit()

        return db_roll_call


@router.delete("/roll_call/delete/{roll_call_id}", tags=["roll_call"])
async def delete_roll_call(user_auth: AuthorizedUser, roll_call_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_roll_call = db.scalars(select(RollCall).where(RollCall.id == roll_call_id)).first()
        if db_roll_call:
            db_roll_call.is_enabled = False
            db.commit()
            return {"massage": f"roll call with id: {roll_call_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="roll call not found!")
