from app.models import Holiday
from app.schemas import HolidayIn, HolidayUpdate, HolidayResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from datetime import date

router = APIRouter(prefix="/holidays")


async def get_by_id(db: SessionDep, holiday_id: int) -> Holiday:
    stored_record = db.get(Holiday, holiday_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[HolidayResponse])
async def get_holidays(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        start: date | None = None,
        end: date | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            Holiday.holiday_date > start if start else True,
            Holiday.holiday_date < end if end else True
        )
        stored_records = db.query(Holiday).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{holiday_id}", response_model=HolidayResponse)
async def get_holiday_by_id(
        db: SessionDep,
        holiday_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, holiday_id)
        return stored_record


@router.post(path="/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
        db: SessionDep,
        data: HolidayIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Holiday(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{holiday_id}", response_model=HolidayResponse)
async def update_holiday(
        db: SessionDep,
        holiday_id: int,
        data: HolidayUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, holiday_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
        db: SessionDep,
        holiday_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, holiday_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
