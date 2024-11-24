from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import PayCategory
from app.schemas import PayCategoryIn, PayCategoryResponse, PayCategoryUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/pay_categories")


# Endpoints of pay category
# add all Endpoints for pay category
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["pay_categories"], response_model=PayCategoryResponse)
async def create_pay_category(
        user_auth: CurrentUser, pay_category: PayCategoryIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["pay_categories"], response_model=list[PayCategoryResponse])
async def get_pay_categories(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            PayCategory.name.contains(search)
            if search else True
        )
        return db.scalars(select(PayCategory).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{pay_category_id}", tags=["pay_categories"], response_model=PayCategoryResponse)
async def get_pay_category_by_id(
        user_auth: CurrentUser, pay_category_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_pay_category = db.scalars(
            select(PayCategory).where(PayCategory.id == pay_category_id)).first()
        if db_pay_category:
            return db_pay_category
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pay category not found!")


@router.put("/{pay_category_id}", tags=["pay_categories"], response_model=PayCategoryResponse)
async def update_pay_category(
        user_auth: CurrentUser,
        pay_category: PayCategoryUpdate,
        pay_category_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{pay_category_id}", tags=["pay_categories"])
async def delete_pay_category(
        user_auth: CurrentUser, pay_category_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_pay_category = db.scalars(
                select(PayCategory).where(PayCategory.id == pay_category_id)).first()
            if db_pay_category:
                db.delete(db_pay_category)
                db.commit()
                return {"massage": f"pay category with id: {pay_category_id} successfully deleted"}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pay category not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")
