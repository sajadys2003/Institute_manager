from app.models import Presentation
from app.schemas import PresentationIn, PresentationUpdate, PresentationResponse

# common modules
from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from sqlalchemy import and_
from app.dependencies import SessionDep, PageDep
from datetime import datetime

router = APIRouter(prefix="/presentations")


async def get_by_id(db: SessionDep, presentation_id: int) -> Presentation:
    criteria = and_(
        Presentation.id == presentation_id,
        Presentation.is_enabled
    )
    stored_record = db.query(Presentation).where(criteria).scalar()
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PresentationResponse])
async def get_all_presentations(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = Presentation.is_enabled

        stored_records = db.query(Presentation).where(criteria).offset(page.offset).limit(page.limit)
        return stored_records.all()


@router.get(path="/{presentation_id}", response_model=PresentationResponse)
async def get_presentation_by_id(
        db: SessionDep,
        presentation_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, presentation_id)
        return stored_record


@router.get("/{teacher_id}", response_model=list[PresentationResponse])
async def get_presentation_by_teacher_id(
        db: SessionDep,
        page: PageDep,
        teacher_id: int,
        current_user: CurrentUer,
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            Presentation.teacher_id == teacher_id,
            Presentation.is_enabled
        )

        stored_records = db.query(Presentation).where(criteria).offset(page.offset).limit(page.limit).all()
        if not stored_records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return stored_records


@router.get("/{course_id}", response_model=list[PresentationResponse])
async def get_presentation_by_course_id(
        db: SessionDep,
        page: PageDep,
        course_id: int,
        current_user: CurrentUer,
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            Presentation.course_id == course_id,
            Presentation.is_enabled
        )

        stored_records = db.query(Presentation).where(criteria).offset(page.offset).limit(page.limit).all()
        if not stored_records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return stored_records


@router.post(path="/", response_model=PresentationResponse, status_code=status.HTTP_201_CREATED)
async def create_presentation(
        db: SessionDep,
        data: PresentationIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        new_record = Presentation(**data_dict)
        db.add(new_record)
        db.commit()
        return new_record


@router.put(path="/{presentation_id}", response_model=PresentationResponse)
async def update_presentation(
        db: SessionDep,
        presentation_id: int,
        data: PresentationUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, presentation_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})

        for key, value in data_dict.items():
            setattr(stored_record, key, value)
        db.commit()

        return stored_record


@router.delete(path="/{presentation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_presentation(
        db: SessionDep,
        presentation_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, presentation_id)
        stored_record.is_enabled = False
        db.commit()
