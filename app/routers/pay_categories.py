from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter
from app.models import PayCategory
from app.schemas import PayCategoryIn, PayCategoryOut, PayCategoryUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of pay category
# add all Endpoints for pay category
# -------------------------------------------------------------------------------------------------------


@router.post("/pay_category/create", tags=["pay_category"], response_model=PayCategoryOut)
async def create_pay_category(
        user_auth: CurrentUser, pay_category: PayCategoryIn, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            pay_category_dict = pay_category.model_dump()
            pay_category_dict["record_date"] = datetime.now()
            pay_category_dict["recorder_id"] = user_auth.id
            db_pay_category = PayCategory(**pay_category_dict)
            db.add(db_pay_category)
            db.commit()
            db.refresh(db_pay_category)
            return db_pay_category
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error adding pay category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding pay category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/pay_category", tags=["pay_category"], response_model=list[PayCategoryOut])
async def get_pay_categories(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(
            PayCategory.name.contains(search)
            if search else True
        )
        return db.scalars(select(PayCategory).where(criteria).limit(pagination.limit).offset(pagination.offset))
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/pay_category/{pay_category_id}", tags=["pay_category"], response_model=PayCategoryOut)
async def get_pay_category(
        user_auth: CurrentUser, pay_category_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_pay_category = db.scalars(
            select(PayCategory).where(PayCategory.id == pay_category_id)).first()
        if db_pay_category:
            return db_pay_category
        raise HTTPException(status_code=404, detail="pay category not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/pay_category/update/{pay_category_id}", tags=["pay_category"], response_model=PayCategoryOut)
async def update_pay_category(
        user_auth: CurrentUser,
        pay_category: PayCategoryUpdate,
        pay_category_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_pay_category = db.scalars(
                select(PayCategory).where(PayCategory.id == pay_category_id)).first()
            if db_pay_category is None:
                raise HTTPException(status_code=404, detail="pay category not found!")
            pay_category_dict = pay_category.model_dump(exclude_unset=True)
            pay_category_dict["record_date"] = datetime.now()
            pay_category_dict["recorder_id"] = user_auth.id
            for key, value in pay_category_dict.items():
                setattr(db_pay_category, key, value)
            db.commit()
            return db_pay_category
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating pay category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating pay category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/pay_category/delete/{pay_category_id}", tags=["pay_category"])
async def delete_pay_category(
        user_auth: CurrentUser, pay_category_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_pay_category = db.scalars(
                select(PayCategory).where(PayCategory.id == pay_category_id)).first()
            if db_pay_category:
                db.delete(db_pay_category)
                db.commit()
                return {"massage": f"pay category with id: {pay_category_id} successfully deleted"}
            else:
                raise HTTPException(status_code=404, detail="pay category not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error deleting pay category {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error deleting pay category {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")
