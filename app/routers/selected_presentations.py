from app.models import SelectedPresentation
from app.schemas import SelectedPresentationIn, SelectedPresentationUpdate, SelectedPresentationResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

router = APIRouter(prefix="/selected_presentations")


async def get_by_id(db: SessionDep, selected_presentation_id: int) -> SelectedPresentation:
    stored_record = db.get(SelectedPresentation, selected_presentation_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[SelectedPresentationResponse])
async def get_selected_presentations(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        presentation_id: int | None = None,
        student_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            SelectedPresentation.presentation_id == presentation_id
            if (presentation_id or presentation_id == 0) else True,

            SelectedPresentation.student_id == student_id
            if (student_id or student_id == 0) else True
        )
        stored_records = db.query(SelectedPresentation).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{selected_presentation_id}", response_model=SelectedPresentationResponse)
async def get_selected_presentation_by_id(
        db: SessionDep,
        selected_presentation_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, selected_presentation_id)
        return stored_record


@router.post(path="/", response_model=SelectedPresentationResponse, status_code=status.HTTP_201_CREATED)
async def create_selected_presentation(
        db: SessionDep,
        data: SelectedPresentationIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if not data.student_id:
            data.student_id = current_user.id

        data_dict = data.model_dump()
        data_dict.update(
            {
                "grade": str(data.grade),
                "recorder_id": current_user.id,
                "record_date": datetime.now()
            }
        )
        try:
            new_record = SelectedPresentation(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{selected_presentation_id}", response_model=SelectedPresentationResponse)
async def update_selected_presentation(
        db: SessionDep,
        selected_presentation_id: int,
        data: SelectedPresentationUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, selected_presentation_id)

        grade = data.grade
        if grade or grade == 0:
            data.grade = str(grade)

        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{selected_presentation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_selected_presentation(
        db: SessionDep,
        selected_presentation_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, selected_presentation_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
