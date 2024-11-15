from app.models import Lesson
from app.schemas import LessonIn, LessonUpdate, LessonResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

router = APIRouter(prefix="/lessons")


async def get_by_id(db: SessionDep, lesson_id: int) -> Lesson:
    stored_record = db.get(Lesson, lesson_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[LessonResponse])
async def get_all_lessons(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer,
        lesson_group_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        q = commons.q
        criteria = and_(
            Lesson.name.ilike(q) if q else True,

            Lesson.lesson_group_id == lesson_group_id
            if (lesson_group_id or lesson_group_id == 0) else True
        )
        stored_records = db.query(Lesson).where(criteria)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{lesson_id}", response_model=LessonResponse)
async def get_lesson_by_id(
        db: SessionDep,
        lesson_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, lesson_id)
        return stored_record


@router.post(path="/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
        db: SessionDep,
        data: LessonIn,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Lesson(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
        db: SessionDep,
        lesson_id: int,
        data: LessonUpdate,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, lesson_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
        db: SessionDep,
        lesson_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, lesson_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
