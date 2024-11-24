from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import PresentationSurvey
from app.schemas import PresentationSurveyIn, PresentationSurveyResponse, PresentationSurveyUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/presentation_surveys")


# Endpoints of presentation survey
# add all Endpoints for presentation survey
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["presentation_surveys"], response_model=PresentationSurveyResponse)
async def create_presentation_survey(
        user_auth: CurrentUser, presentation_survey: PresentationSurveyIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            presentation_survey_dict = presentation_survey.model_dump()
            presentation_survey_dict["record_date"] = datetime.now()
            presentation_survey_dict["recorder_id"] = user_auth.id
            db_presentation_survey = PresentationSurvey(**presentation_survey_dict)
            db.add(db_presentation_survey)
            db.commit()
            db.refresh(db_presentation_survey)
            return db_presentation_survey
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"{e.args}")


@router.get("/", tags=["presentation_surveys"], response_model=list[PresentationSurveyResponse])
async def get_presentation_surveys(
        user_auth: CurrentUser,
        pagination: PageDep,
        db: Session = Depends(get_session),
        student_id: int | None = None,
        presentation_id: int | None = None,
        survey_category_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            PresentationSurvey.student_id == student_id
            if (student_id or student_id == 0) else True,
            PresentationSurvey.presentation_id == presentation_id
            if (presentation_id or presentation_id == 0) else True,
            PresentationSurvey.survey_category_id == survey_category_id
            if (survey_category_id or survey_category_id == 0) else True
        )
        return db.scalars(select(PresentationSurvey).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{presentation_survey_id}", tags=["presentation_surveys"], response_model=PresentationSurveyResponse)
async def get_presentation_survey_by_id(
        user_auth: CurrentUser, presentation_survey_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_presentation_survey = db.scalars(
            select(PresentationSurvey).where(PresentationSurvey.id == presentation_survey_id)).first()
        if db_presentation_survey:
            return db_presentation_survey
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="presentation survey not found!")


@router.put("/{presentation_survey_id}", tags=["presentation_surveys"], response_model=PresentationSurveyResponse)
async def update_presentation_surveys(
        user_auth: CurrentUser,
        presentation_survey: PresentationSurveyUpdate,
        presentation_survey_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_presentation_survey = db.scalars(
                select(PresentationSurvey).where(PresentationSurvey.id == presentation_survey_id)).first()
            if db_presentation_survey is None:
                raise HTTPException(status_code=404, detail="presentation survey not found!")
            presentation_survey_dict = presentation_survey.model_dump(exclude_unset=True)
            presentation_survey_dict["record_date"] = datetime.now()
            presentation_survey_dict["recorder_id"] = user_auth.id
            for key, value in presentation_survey_dict.items():
                setattr(db_presentation_survey, key, value)
            db.commit()
            return db_presentation_survey
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{presentation_survey_id}", tags=["presentation_surveys"])
async def delete_presentation_survey(
        user_auth: CurrentUser, presentation_survey_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_presentation_survey = db.scalars(
            select(PresentationSurvey).where(PresentationSurvey.id == presentation_survey_id)).first()
        if db_presentation_survey:
            db.delete(db_presentation_survey)
            db.commit()
            return {"massage": f"presentation survey with id: {presentation_survey_id} successfully deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="presentation survey not found!")
