from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import SurveyCategory
from app.schemas import SurveyCategoryIn, SurveyCategoryResponse, SurveyCategoryUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/survey_categories")


# Endpoints of survey category
# add all Endpoints for survey category
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["survey_categories"], response_model=SurveyCategoryResponse)
async def create_survey_category(
        user_auth: CurrentUser, survey_category: SurveyCategoryIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            survey_category_dict = survey_category.model_dump()
            survey_category_dict["record_date"] = datetime.now()
            survey_category_dict["recorder_id"] = user_auth.id
            db_survey_category = SurveyCategory(**survey_category_dict)
            db.add(db_survey_category)
            db.commit()
            db.refresh(db_survey_category)
            return db_survey_category
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["survey_categories"], response_model=list[SurveyCategoryResponse])
async def get_survey_categories(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            SurveyCategory.name.contains(search)
            if search else True
        )
        return db.scalars(select(SurveyCategory).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{survey_category_id}", tags=["survey_categories"], response_model=SurveyCategoryResponse)
async def get_survey_category_by_id(
        user_auth: CurrentUser,
        survey_category_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_survey_category = db.scalars(
            select(SurveyCategory).where(SurveyCategory.id == survey_category_id)).first()
        if db_survey_category:
            return db_survey_category
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="survey category not found!")


@router.put("/{survey_category_id}", tags=["survey_categories"], response_model=SurveyCategoryResponse)
async def update_survey_category(
        user_auth: CurrentUser,
        survey_category: SurveyCategoryUpdate,
        survey_category_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_survey_category = db.scalars(
                select(SurveyCategory).where(SurveyCategory.id == survey_category_id)).first()
            if db_survey_category is None:
                raise HTTPException(status_code=404, detail="survey category not found!")
            survey_category_dict = survey_category.model_dump(exclude_unset=True)
            survey_category_dict["record_date"] = datetime.now()
            survey_category_dict["recorder_id"] = user_auth.id
            for key, value in survey_category_dict.items():
                setattr(db_survey_category, key, value)
            db.commit()
            return db_survey_category
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")


@router.delete("/{survey_category_id}", tags=["survey_categories"])
async def delete_survey_category(
        user_auth: CurrentUser,
        survey_category_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_survey_category = db.scalars(
                select(SurveyCategory).where(SurveyCategory.id == survey_category_id)).first()
            if db_survey_category:
                db.delete(db_survey_category)
                db.commit()
                return {"massage": f"survey category with id: {survey_category_id} successfully deleted"}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="survey category not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")
