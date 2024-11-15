from inspect import currentframe
from fastapi import Depends, HTTPException
from app.models import PresentationSurvey
from app.schemas import PresentationSurveyIn, PresentationSurveyResponse, PresentationSurveyUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, or_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of survey category
# add all Endpoints for survey category
# -------------------------------------------------------------------------------------------------------


@router.post("/presentation_survey/create", tags=["presentation_survey"], response_model=PresentationSurveyResponse)
async def create_presentation_survey(
        user_auth: CurrentUser, survey_category: PresentationSurveyIn, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            presentation_survey_dict = survey_category.dict()
            presentation_survey_dict["record_date"] = datetime.now()
            presentation_survey_dict["recorder_id"] = user_auth.id
            db_presentation_survey = PresentationSurvey(**presentation_survey_dict)
            db.add(db_presentation_survey)
            db.commit()
            db.refresh(db_presentation_survey)
            return db_presentation_survey
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error adding presentation survey {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding presentation survey {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/presentation_survey", tags=["presentation_survey"], response_model=list[PresentationSurveyResponse])
async def get_presentation_survey(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        if search:
            presentation_survey = db.scalars(select(PresentationSurvey).where(or_(
                PresentationSurvey.student_id == search,
                PresentationSurvey.presentation_id == search)).limit(pagination.limit).offset(pagination.offset))
            if presentation_survey:
                return presentation_survey
            raise HTTPException(status_code=404, detail="presentation survey not found!")
        presentation_survey = db.scalars(
            select(PresentationSurveyResponse).limit(pagination.limit).offset(pagination.offset))
        if presentation_survey:
            return presentation_survey
        raise HTTPException(status_code=404, detail="presentation survey not found")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/presentation_survey/{presentation_survey_id}", tags=["presentation_survey"],
            response_model=PresentationSurveyResponse)
async def get_presentation_survey(
        user_auth: CurrentUser, presentation_survey_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_presentation_survey = db.scalars(
            select(PresentationSurvey).where(PresentationSurvey.id == presentation_survey_id)).first()
        if db_presentation_survey:
            return db_presentation_survey
        raise HTTPException(status_code=404, detail="presentation survey not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/presentation_survey/update/{presentation_survey_id}", tags=["presentation_survey"],
            response_model=PresentationSurveyResponse)
async def update_presentation_survey(
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
                setattr(presentation_survey, key, value)
            db.commit()
            return db_presentation_survey
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating presentation survey {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating presentation survey {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/presentation_survey/delete/{presentation_survey_id}", tags=["presentation_survey"])
async def delete_presentation_survey(
        user_auth: CurrentUser, presentation_survey_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_presentation_survey = db.scalars(
            select(PresentationSurvey).where(PresentationSurvey.id == presentation_survey_id)).first()
        if db_presentation_survey:
            db.delete(db_presentation_survey)
            db.commit()
            return {"massage": f"presentation survey with id: {presentation_survey_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="presentation survey not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
