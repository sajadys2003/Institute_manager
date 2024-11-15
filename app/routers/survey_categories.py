from app.models import SurveyCategory
from app.schemas import SurveyCategoryIn, SurveyCategoryUpdate, SurveyCategoryResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/survey_categories")


async def get_by_id(db: SessionDep, survey_category_id: int) -> SurveyCategory:
    stored_record = db.get(SurveyCategory, survey_category_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[SurveyCategoryResponse])
async def get_all_survey_categories(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = SurveyCategory.name.ilike(q)
            stored_records = db.query(SurveyCategory).where(criteria)

        else:
            stored_records = db.query(SurveyCategory)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{survey_category_id}", response_model=SurveyCategoryResponse)
async def get_survey_category_by_id(
        db: SessionDep,
        survey_category_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, survey_category_id)
        return stored_record


@router.post(path="/", response_model=SurveyCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_survey_category(
        db: SessionDep,
        data: SurveyCategoryIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = SurveyCategory(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{survey_category_id}", response_model=SurveyCategoryResponse)
async def update_survey_category(
        db: SessionDep,
        survey_category_id: int,
        data: SurveyCategoryUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, survey_category_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{survey_category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey_category(
        db: SessionDep,
        survey_category_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, survey_category_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
