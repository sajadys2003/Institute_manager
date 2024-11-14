from app.models import FinancialCategory
from app.schemas import FinancialCategoryIn, FinancialCategoryUpdate, FinancialCategoryResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/financial_categories")


async def get_by_id(db: SessionDep, financial_category_id: int) -> FinancialCategory:
    stored_record = db.get(FinancialCategory, financial_category_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[FinancialCategoryResponse])
async def get_all_financial_categories(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = FinancialCategory.name.contains(q)
            stored_records = db.query(FinancialCategory).where(criteria)

        else:
            stored_records = db.query(FinancialCategory)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{financial_category_id}", response_model=FinancialCategoryResponse)
async def get_financial_category_by_id(
        db: SessionDep,
        financial_category_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, financial_category_id)
        return stored_record


@router.post(path="/", response_model=FinancialCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_financial_category(
        db: SessionDep,
        data: FinancialCategoryIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = FinancialCategory(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{financial_category_id}", response_model=FinancialCategoryResponse)
async def update_financial_category(
        db: SessionDep,
        financial_category_id: int,
        data: FinancialCategoryUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, financial_category_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{financial_category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_financial_category(
        db: SessionDep,
        financial_category_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, financial_category_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
