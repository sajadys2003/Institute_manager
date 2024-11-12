from fastapi import Depends, HTTPException
from app.models import SurveyCategory
from app.schemas import SurveyCategoryIn, SurveyCategoryResponse, SurveyCategoryUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_, or_
from app.routers.security import CurrentUser

router = APIRouter()


# Endpoints of survey category
# add all Endpoints for survey category
# -------------------------------------------------------------------------------------------------------


@router.post("/survey_category/create", tags=["survey_category"], response_model=SurveyCategoryResponse)
async def create_survey_category(
        user_auth: CurrentUser, survey_category: SurveyCategoryIn, db: Session = Depends(get_session)
):
    if user_auth:
        survey_category_dict = survey_category.dict()
        survey_category_dict["record_date"] = datetime.now()
        survey_category_dict["recorder_id"] = user_auth.id
        db_survey_category = SurveyCategory(**survey_category_dict)
        db.add(db_survey_category)
        db.commit()
        db.refresh(db_survey_category)
        return db_survey_category
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/survey_category", tags=["survey_category"], response_model=list[SurveyCategoryResponse])
async def get_survey_category(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth:
        if search:
            criteria = and_(SurveyCategory.is_enabled, or_(SurveyCategory.name.contains(search)))
            survey_category = db.scalars(
                select(SurveyCategory).where(criteria).limit(pagination.limit).offset(pagination.offset))
            if survey_category:
                return survey_category
            raise HTTPException(status_code=404, detail="survey category not found!")
        survey_categories = db.scalars(select(SurveyCategory).limit(pagination.limit).offset(pagination.offset))
        if survey_categories:
            return survey_categories
        raise HTTPException(status_code=404, detail="survey category not found")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/survey_category/{survey_category_id}", tags=["survey_category"], response_model=SurveyCategoryResponse)
async def get_survey_category(user_auth: CurrentUser, survey_category_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_survey_category = db.scalars(
            select(SurveyCategory).where(SurveyCategory.id == survey_category_id).
            where(SurveyCategory.is_enabled)).first()
        if db_survey_category:
            return db_survey_category
        raise HTTPException(status_code=404, detail="survey category not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put(
    "/survey_category/update/{survey_category_id}", tags=["survey_category"], response_model=SurveyCategoryResponse
)
async def update_survey_category(
        user_auth: CurrentUser,
        survey_category: SurveyCategoryUpdate,
        survey_category_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:
        db_survey_category = db.scalars(
            select(SurveyCategory).where(SurveyCategory.id == survey_category_id).
            where(SurveyCategory.is_enabled)).first()
        if db_survey_category is None:
            raise HTTPException(status_code=404, detail="survey category not found!")
        survey_category_dict = survey_category.model_dump(exclude_unset=True)
        survey_category_dict["record_date"] = datetime.now()
        survey_category_dict["recorder_id"] = user_auth.id
        for key, value in survey_category_dict.items():
            setattr(survey_category, key, value)
        db.commit()
        return db_survey_category
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/survey_category/delete/{survey_category_id}", tags=["survey_category"])
async def delete_survey_category(user_auth: CurrentUser, survey_category_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_survey_category = db.scalars(
            select(SurveyCategory).where(SurveyCategory.id == survey_category_id).
            where(SurveyCategory.is_enabled)).first()
        if db_survey_category:
            db_survey_category.is_enabled = False
            db.commit()
            return {"massage": f"survey category with id: {survey_category_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="survey category not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
