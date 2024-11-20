from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter
from app.models import SurveyCategory
from app.schemas import SurveyCategoryIn, SurveyCategoryOut, SurveyCategoryUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of survey category
# add all Endpoints for survey category
# -------------------------------------------------------------------------------------------------------


@router.post("/survey_category/create", tags=["survey_category"], response_model=SurveyCategoryOut)
async def create_survey_category(
        user_auth: CurrentUser, survey_category: SurveyCategoryIn, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
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
            raise HTTPException(status_code=400, detail=f"integrity error adding survey category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding survey category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/survey_category", tags=["survey_category"], response_model=list[SurveyCategoryOut])
async def get_survey_categories(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(
            SurveyCategory.name.contains(search)
            if search else True
        )
        return db.scalars(select(SurveyCategory).where(criteria).limit(pagination.limit).offset(pagination.offset))
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/survey_category/{survey_category_id}", tags=["survey_category"], response_model=SurveyCategoryOut)
async def get_survey_category(user_auth: CurrentUser, survey_category_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_survey_category = db.scalars(
            select(SurveyCategory).where(SurveyCategory.id == survey_category_id)).first()
        if db_survey_category:
            return db_survey_category
        raise HTTPException(status_code=404, detail="survey category not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put(
    "/survey_category/update/{survey_category_id}", tags=["survey_category"], response_model=SurveyCategoryOut)
async def update_survey_category(
        user_auth: CurrentUser,
        survey_category: SurveyCategoryUpdate,
        survey_category_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
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
            raise HTTPException(status_code=400, detail=f"integrity error updating survey category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating survey category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/survey_category/delete/{survey_category_id}", tags=["survey_category"])
async def delete_survey_category(user_auth: CurrentUser, survey_category_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_survey_category = db.scalars(
                select(SurveyCategory).where(SurveyCategory.id == survey_category_id)).first()
            if db_survey_category:
                db.delete(db_survey_category)
                db.commit()
                return {"massage": f"survey category with id: {survey_category_id} successfully deleted"}
            else:
                raise HTTPException(status_code=404, detail="survey category not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error deleting survey category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error deleting survey category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")
