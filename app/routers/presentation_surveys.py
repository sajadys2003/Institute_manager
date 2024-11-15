from app.models import PresentationSurvey, Presentation
from app.schemas import PresentationSurveyIn, PresentationSurveyUpdate, PresentationSurveyResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

router = APIRouter(prefix="/presentation_surveys")


async def get_by_id(db: SessionDep, presentation_survey_id: int) -> PresentationSurveyResponse:
    stored_record = db.get(PresentationSurvey, presentation_survey_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PresentationSurveyResponse])
async def get_all_presentation_surveys(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        student_id: int | None = None,
        presentation_id: int | None = None,
        survey_category_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            PresentationSurvey.student_id == student_id
            if (student_id or student_id == 0) else True,

            PresentationSurvey.presentation_id == presentation_id
            if (presentation_id or presentation_id == 0) else True,

            PresentationSurvey.survey_category_id == survey_category_id
            if (survey_category_id or survey_category_id == 0) else True
        )
        stored_records = db.query(PresentationSurvey).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{presentation_survey_id}", response_model=PresentationSurveyResponse)
async def get_presentation_survey_by_id(
        db: SessionDep,
        presentation_survey_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, presentation_survey_id)
        return stored_record


@router.post(path="/", response_model=PresentationSurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_presentation_survey(
        db: SessionDep,
        data: PresentationSurveyIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = PresentationSurvey(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{presentation_survey_id}", response_model=PresentationSurveyResponse)
async def update_presentation_survey(
        db: SessionDep,
        presentation_session_id: int,
        data: PresentationSurveyUpdate,
        current_user: CurrentUer
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


@router.delete(path="/{presentation_survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_presentation_survey(
        db: SessionDep,
        presentation_survey_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, presentation_survey_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
