from app.models import Presentation
from app.schemas import PresentationIn, PresentationUpdate, PresentationResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/presentations")


async def get_by_id(db: SessionDep, presentation_id: int) -> Presentation:
    stored_record = db.get(Presentation, presentation_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PresentationResponse])
async def get_all_presentations(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        course_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if course_id:
            criteria = Presentation.course_id == course_id
            stored_records = db.query(Presentation).where(criteria)

        else:
            stored_records = db.query(Presentation)
        return stored_records.offset(page.offset).limit(page.limit).all()


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


@router.post(path="/", response_model=PresentationResponse, status_code=status.HTTP_201_CREATED)
async def create_presentation(
        db: SessionDep,
        data: PresentationIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if not data.date:
            data.date = datetime.now()

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Presentation(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


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
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{presentation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_presentation(
        db: SessionDep,
        presentation_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, presentation_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
