from app.models import CoursePrerequisite
from app.schemas import CoursePrerequisiteIn, CoursePrerequisiteUpdate, CoursePrerequisiteResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

router = APIRouter(prefix="/course_prerequisites")


async def get_by_id(db: SessionDep, main_course_id: int, prerequisite_id: int) -> CoursePrerequisite:
    stored_record = db.get(CoursePrerequisite, [main_course_id, prerequisite_id])
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[CoursePrerequisiteResponse])
async def get_all_course_prerequisites(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        main_course_id: int | None = None,
        prerequisite_id: int | None = None,
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            CoursePrerequisite.main_course_id == main_course_id
            if (main_course_id or main_course_id == 0) else True,

            CoursePrerequisite.prerequisite_id == prerequisite_id
            if (prerequisite_id or prerequisite_id == 0) else True
        )
        stored_records = db.query(CoursePrerequisite).where(criteria)
        return stored_records.offset(page.offset).limit(page.limit).all()


@router.post(path="/", response_model=CoursePrerequisiteResponse, status_code=status.HTTP_201_CREATED)
async def create_course_prerequisite(
        db: SessionDep,
        data: CoursePrerequisiteIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = CoursePrerequisite(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/", response_model=CoursePrerequisiteResponse)
async def update_course_prerequisite(
        db: SessionDep,
        main_course_id: int,
        prerequisite_id: int,
        data: CoursePrerequisiteUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, main_course_id, prerequisite_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_prerequisite(
        db: SessionDep,
        main_course_id: int,
        prerequisite_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, main_course_id, prerequisite_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
