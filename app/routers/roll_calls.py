from app.models import RollCall
from app.schemas import RollCallIn, RollCallUpdate, RollCallResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

router = APIRouter(prefix="/roll_calls")


async def get_by_id(db: SessionDep, roll_call_id: int) -> RollCall:
    stored_record = db.get(RollCall, roll_call_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[RollCallResponse])
async def get_all_roll_calls(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        presentation_session_id: int | None = None,
        student_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            RollCall.presentation_session_id == presentation_session_id
            if (presentation_session_id or presentation_session_id == 0) else True,

            RollCall.student_id == student_id
            if (student_id or student_id == 0) else True
        )
        stored_records = db.query(RollCall).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{roll_call_id}", response_model=RollCallResponse)
async def get_roll_call_by_id(
        db: SessionDep,
        roll_call_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, roll_call_id)
        return stored_record


@router.post(path="/", response_model=RollCallResponse, status_code=status.HTTP_201_CREATED)
async def create_roll_call(
        db: SessionDep,
        data: RollCallIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = RollCall(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{roll_call_id}", response_model=RollCallResponse)
async def update_roll_call(
        db: SessionDep,
        roll_call_id: int,
        data: RollCallUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, roll_call_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{roll_call_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roll_call(
        db: SessionDep,
        roll_call_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, roll_call_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
