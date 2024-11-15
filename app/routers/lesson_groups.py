from app.models import LessonGroup
from app.schemas import LessonGroupIn, LessonGroupUpdate, LessonGroupResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/lesson_groups")


async def get_by_id(db: SessionDep, lesson_group_id: int) -> LessonGroup:
    stored_record = db.get(LessonGroup, lesson_group_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[LessonGroupResponse])
async def get_all_lesson_groups(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = LessonGroup.name.ilike(q)
            stored_records = db.query(LessonGroup).where(criteria)

        else:
            stored_records = db.query(LessonGroup)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{lesson_group_id}", response_model=LessonGroupResponse)
async def get_lesson_group_by_id(
        db: SessionDep,
        lesson_group_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, lesson_group_id)
        return stored_record


@router.post(path="/", response_model=LessonGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson_group(
        db: SessionDep,
        data: LessonGroupIn,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = LessonGroup(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{lesson_group_id}", response_model=LessonGroupResponse)
async def update_lesson_group(
        db: SessionDep,
        lesson_group_id: int,
        data: LessonGroupUpdate,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, lesson_group_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{lesson_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_group(
        db: SessionDep,
        lesson_group_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, lesson_group_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
