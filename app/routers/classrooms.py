from app.models import Classroom
from app.schemas import ClassroomIn, ClassroomUpdate, ClassroomResponse

# common modules
from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from sqlalchemy import and_
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime

router = APIRouter(prefix="/classrooms")


async def get_by_id(db: SessionDep, classroom_id: int) -> Classroom:
    criteria = and_(
        Classroom.id == classroom_id,
        Classroom.is_enabled
    )
    stored_record = db.query(Classroom).where(criteria).scalar()

    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[ClassroomResponse])
async def get_all_classrooms(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = and_(
                Classroom.is_enabled,
                Classroom.name.contains(q)
            )
        else:
            criteria = Classroom.is_enabled

        stored_records = db.query(Classroom).where(criteria).offset(commons.offset).limit(commons.limit)
        return stored_records.all()


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
        new_record = Classroom(**data_dict)
        db.add(new_record)
        db.commit()
        return new_record


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

        for key, value in data_dict.items():
            setattr(stored_record, key, value)
        db.commit()

        return stored_record


@router.delete(path="/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(
        db: SessionDep,
        classroom_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, classroom_id)
        stored_record.is_enabled = False
        db.commit()
