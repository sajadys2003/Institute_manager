from app.models import Classroom
from app.schemas import ClassroomIn, ClassroomUpdate, ClassroomResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

router = APIRouter(prefix="/classrooms")


async def get_by_id(db: SessionDep, lesson_id: int) -> Classroom:
    stored_record = db.get(Classroom, lesson_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[ClassroomResponse])
async def get_all_classrooms(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer,
        building_id: int | None = None,
        lesson_group_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        q = commons.q
        criteria = and_(
            Classroom.name.ilike(q) if q else True,

            Classroom.building_id == building_id
            if (building_id or building_id == 0) else True,

            Classroom.lesson_group_id == lesson_group_id
            if (lesson_group_id or lesson_group_id == 0) else True
        )
        stored_records = db.query(Classroom).where(criteria)

        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom_by_id(
        db: SessionDep,
        classroom_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, classroom_id)
        return stored_record


@router.post(path="/", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
async def create_classroom(
        db: SessionDep,
        data: ClassroomIn,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Classroom(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
        db: SessionDep,
        classroom_id: int,
        data: ClassroomUpdate,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, classroom_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(
        db: SessionDep,
        classroom_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, classroom_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
