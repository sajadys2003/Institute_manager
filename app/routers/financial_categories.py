from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import FinancialCategory
from app.schemas import FinancialCategoryIn, FinancialCategoryResponse, FinancialCategoryUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/financial_categories")


# Endpoints of financial category
# add all Endpoints for financial category
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["financial_categories"], response_model=FinancialCategoryResponse)
async def create_financial_category(
        user_auth: CurrentUser, financial_category: FinancialCategoryIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            financial_category_dict = financial_category.model_dump()
            financial_category_dict["record_date"] = datetime.now()
            financial_category_dict["recorder_id"] = user_auth.id
            db_financial_category = FinancialCategory(**financial_category_dict)
            db.add(db_financial_category)
            db.commit()
            db.refresh(db_financial_category)
            return db_financial_category
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["financial_categories"], response_model=list[FinancialCategoryResponse])
async def get_financial_categories(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            FinancialCategory.name.contains(search)
            if search else True
        )
        return db.scalars(select(FinancialCategory).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{financial_category_id}", tags=["financial_categories"], response_model=FinancialCategoryResponse)
async def get_financial_category_by_id(
        user_auth: CurrentUser, financial_category_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_financial_category = db.scalars(
            select(FinancialCategory).where(FinancialCategory.id == financial_category_id)).first()
        if db_financial_category:
            return db_financial_category
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="financial category not found!")


@router.put("/{financial_category_id}", tags=["financial_categories"], response_model=FinancialCategoryResponse)
async def update_financial_category(
        user_auth: CurrentUser,
        financial_category: FinancialCategoryUpdate,
        financial_category_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_financial_category = db.scalars(
                select(FinancialCategory).where(FinancialCategory.id == financial_category_id)).first()
            if db_financial_category is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="financial category not found!")
            financial_category_dict = financial_category.model_dump(exclude_unset=True)
            financial_category_dict["record_date"] = datetime.now()
            financial_category_dict["recorder_id"] = user_auth.id
            for key, value in financial_category_dict.items():
                setattr(db_financial_category, key, value)
            db.commit()
            return db_financial_category
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{financial_category_id}", tags=["financial_categories"])
async def delete_financial_category(
        user_auth: CurrentUser, financial_category_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_financial_category = db.scalars(
                select(FinancialCategory).where(FinancialCategory.id == financial_category_id)).first()
            if db_financial_category:
                db.delete(db_financial_category)
                db.commit()
                return {"massage": f"financial category with id: {financial_category_id} successfully deleted"}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="financial category not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")
