from app.models import Course
from app.schemas import CourseIn, CourseUpdate, CourseResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/courses")


async def get_by_id(db: SessionDep, course_id: int) -> Course:
    stored_record = db.get(Course, course_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[CourseResponse])
async def get_all_courses(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = Course.name.contains(q)
            stored_records = db.query(Course).where(criteria)

        else:
            stored_records = db.query(Course)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{course_id}", response_model=CourseResponse)
async def get_course_by_id(
        db: SessionDep,
        course_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, course_id)
        return stored_record


@router.post(path="/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
        db: SessionDep,
        data: CourseIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Course(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{course_id}", response_model=CourseResponse)
async def update_course(
        db: SessionDep,
        course_id: int,
        data: CourseUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, course_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
        db: SessionDep,
        course_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, course_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
