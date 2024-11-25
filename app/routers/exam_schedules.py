from app.models import ExamSchedule
from app.schemas import ExamScheduleIn, ExamScheduleUpdate, ExamScheduleResponse

from .security import CurrentUser, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_

router = APIRouter(prefix="/exam_schedules", tags=["exam_schedules"])


async def get_by_id(db: SessionDep, exam_schedule_id: int) -> ExamSchedule:
    stored_record = db.get(ExamSchedule, exam_schedule_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[ExamScheduleResponse])
async def get_exam_schedules(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUser,
        exam_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            ExamSchedule.exam_id == exam_id
            if (exam_id or exam_id == 0) else True,

            ExamSchedule.start_date > from_date if from_date else True,
            ExamSchedule.start_date < to_date if to_date else True
        )
        stored_records = db.query(ExamSchedule).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{exam_schedule_id}", response_model=ExamScheduleResponse)
async def get_exam_schedule(
        db: SessionDep,
        exam_schedule_id: int,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, exam_schedule_id)
        return stored_record


@router.post(path="/", response_model=ExamScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_exam_schedule(
        db: SessionDep,
        data: ExamScheduleIn,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = ExamSchedule(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except (IntegrityError, SQLAlchemyError) as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{exam_schedule_id}", response_model=ExamScheduleResponse)
async def update_exam_schedule(
        db: SessionDep,
        exam_schedule_id: int,
        data: ExamScheduleUpdate,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, exam_schedule_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except (IntegrityError, SQLAlchemyError) as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{exam_schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam_schedule(
        db: SessionDep,
        exam_schedule_id: int,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, exam_schedule_id)
        try:
            db.delete(stored_record)
            db.commit()
        except (IntegrityError, SQLAlchemyError) as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
