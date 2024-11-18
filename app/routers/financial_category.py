from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter
from app.models import FinancialCategory
from app.schemas import FinancialCategoryIn, FinancialCategoryOut, FinancialCategoryUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of financial category
# add all Endpoints for financial category
# -------------------------------------------------------------------------------------------------------


@router.post("/financial_category/create", tags=["financial_category"], response_model=FinancialCategoryOut)
async def create_financial_category(
        user_auth: CurrentUser, financial_category: FinancialCategoryIn, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
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
            raise HTTPException(status_code=400, detail=f"integrity error adding financial category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding financial category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/financial_category", tags=["financial_category"], response_model=list[FinancialCategoryOut])
async def get_financial_categories(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(
            FinancialCategory.name.contains(search)
            if search else True
        )
        return db.scalars(select(FinancialCategory).where(criteria).limit(pagination.limit).offset(pagination.offset))
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/financial_category/{financial_category_id}", tags=["financial_category"],
            response_model=FinancialCategoryOut)
async def get_financial_category(
        user_auth: CurrentUser, financial_category_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_financial_category = db.scalars(
            select(FinancialCategory).where(FinancialCategory.id == financial_category_id)).first()
        if db_financial_category:
            return db_financial_category
        raise HTTPException(status_code=404, detail="financial category not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/financial_category/update/{financial_category_id}", tags=["financial_category"],
            response_model=FinancialCategoryOut)
async def update_financial_category(
        user_auth: CurrentUser,
        financial_category: FinancialCategoryUpdate,
        financial_category_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_financial_category = db.scalars(
                select(FinancialCategory).where(FinancialCategory.id == financial_category_id)).first()
            if db_financial_category is None:
                raise HTTPException(status_code=404, detail="financial category not found!")
            financial_category_dict = financial_category.model_dump(exclude_unset=True)
            financial_category_dict["record_date"] = datetime.now()
            financial_category_dict["recorder_id"] = user_auth.id
            for key, value in financial_category_dict.items():
                setattr(db_financial_category, key, value)
            db.commit()
            return db_financial_category
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating financial category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating financial category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/financial_category/delete/{financial_category_id}", tags=["financial_category"])
async def delete_financial_category(
        user_auth: CurrentUser, financial_category_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_financial_category = db.scalars(
                select(FinancialCategory).where(FinancialCategory.id == financial_category_id)).first()
            if db_financial_category:
                db.delete(db_financial_category)
                db.commit()
                return {"massage": f"financial category with id: {financial_category_id} successfully deleted"}
            else:
                raise HTTPException(status_code=404, detail="financial category not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error deleting financial category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error deleting financial category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")
