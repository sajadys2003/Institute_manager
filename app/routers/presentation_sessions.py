from app.models import PresentationSession
from app.schemas import PresentationSessionIn, PresentationSessionUpdate, PresentationSessionResponse

from .security import CurrentUser, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_

router = APIRouter(prefix="/presentation_sessions", tags=["presentation_sessions"])


async def get_by_id(db: SessionDep, presentation_session_id: int) -> PresentationSession:
    stored_record = db.get(PresentationSession, presentation_session_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PresentationSessionResponse])
async def get_presentation_sessions(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUser,
        presentation_id: int | None = None,
        classroom_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            PresentationSession.presentation_id == presentation_id
            if (presentation_id or presentation_id == 0) else True,

            PresentationSession.classroom_id == classroom_id
            if (classroom_id or classroom_id == 0) else True,

            PresentationSession.start_time > from_date if from_date else True,
            PresentationSession.start_time < to_date if to_date else True
        )
        stored_records = db.query(PresentationSession).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{presentation_session_id}", response_model=PresentationSessionResponse)
async def get_presentation_session(
        db: SessionDep,
        presentation_session_id: int,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, presentation_session_id)
        return stored_record


@router.post(path="/", response_model=PresentationSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_presentation_session(
        db: SessionDep,
        data: PresentationSessionIn,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = PresentationSession(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except (IntegrityError, SQLAlchemyError) as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{presentation_session_id}", response_model=PresentationSessionResponse)
async def update_presentation_session(
        db: SessionDep,
        presentation_session_id: int,
        data: PresentationSessionUpdate,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, presentation_session_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{presentation_session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_presentation_session(
        db: SessionDep,
        presentation_session_id: int,
        current_user: CurrentUser
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, presentation_session_id)
        try:
            db.delete(stored_record)
            db.commit()
        except (IntegrityError, SQLAlchemyError) as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
