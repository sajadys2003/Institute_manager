from inspect import currentframe
from fastapi import Depends, HTTPException
from app.models import FinancialTransaction
from app.schemas import FinancialTransactionIn, FinancialTransactionResponse, FinancialTransactionUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, or_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of financial transaction
# add all Endpoints for financial transaction
# -------------------------------------------------------------------------------------------------------


@router.post("/financial_transaction/create", tags=["financial_transaction"],
             response_model=FinancialTransactionResponse)
async def create_financial_transaction(
        user_auth: CurrentUser, financial_transaction: FinancialTransactionIn, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            x = 0
            financial_transaction_dict = financial_transaction.dict()
            if financial_transaction_dict["presentation_id"]:
                x += 1
            if financial_transaction_dict["selected_presentation_id"]:
                x += 1
            if financial_transaction_dict["selected_exam_id"]:
                x += 1
            if x == 1:
                financial_transaction_dict["record_date"] = datetime.now()
                financial_transaction_dict["recorder_id"] = user_auth.id
                db_financial_transaction = FinancialTransaction(**financial_transaction_dict)
                db.add(db_financial_transaction)
                db.commit()
                db.refresh(db_financial_transaction)
                return db_financial_transaction
            raise HTTPException(
                status_code=400,
                detail="one of presentation_id , selected_presentation_id and selected_exam_id must enter")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error adding financial transaction {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding financial transaction {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/financial_transaction", tags=["financial_transaction"],
            response_model=list[FinancialTransactionResponse])
async def get_financial_transactions(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: int | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        if search:
            financial_transaction = db.scalars(
                select(FinancialTransaction).where(or_(
                    FinancialTransaction.user_id == search,
                    FinancialTransaction.presentation_id == search,
                    FinancialTransaction.selected_presentation_id == search,
                    FinancialTransaction.selected_exam_id == search)).limit(pagination.limit).offset(pagination.offset))
            if financial_transaction:
                return financial_transaction
            raise HTTPException(status_code=404, detail="financial transaction not found!")
        financial_transaction = db.scalars(
            select(FinancialTransaction).limit(pagination.limit).offset(pagination.offset))
        if financial_transaction:
            return financial_transaction
        raise HTTPException(status_code=404, detail="financial transaction not found")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/financial_transaction/{financial_transaction_id}", tags=["financial_transaction"],
            response_model=FinancialTransactionResponse)
async def get_financial_transaction(
        user_auth: CurrentUser, financial_transaction_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_financial_transaction = db.scalars(
            select(FinancialTransaction).where(FinancialTransaction.id == financial_transaction_id)).first()
        if db_financial_transaction:
            return db_financial_transaction
        raise HTTPException(status_code=404, detail="financial transaction not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/financial_transaction/update/{financial_transaction_id}", tags=["financial_transaction"],
            response_model=FinancialTransactionResponse)
async def update_financial_transaction(
        user_auth: CurrentUser,
        financial_transaction: FinancialTransactionUpdate,
        financial_transaction_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_financial_transaction = db.scalars(
                select(FinancialTransaction).where(FinancialTransaction.id == financial_transaction_id)).first()
            if db_financial_transaction is None:
                raise HTTPException(status_code=404, detail="financial transaction not found!")
            x = 0
            financial_transaction_dict = financial_transaction.model_dump(exclude_unset=True)
            if financial_transaction_dict["presentation_id"]:
                x += 1
            if financial_transaction_dict["selected_presentation_id"]:
                x += 1
            if financial_transaction_dict["selected_exam_id"]:
                x += 1
            if x == 1 or x == 0:
                financial_transaction_dict["record_date"] = datetime.now()
                financial_transaction_dict["recorder_id"] = user_auth.id
                for key, value in financial_transaction_dict.items():
                    setattr(db_financial_transaction, key, value)
                db.commit()
                return financial_transaction
            raise HTTPException(
                status_code=400,
                detail="one of presentation_id , selected_presentation_id and selected_exam_id must enter")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating financial transaction {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating financial transaction {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/financial_transaction/delete/{financial_transaction_id}", tags=["financial_transaction"])
async def delete_financial_transaction(
        user_auth: CurrentUser, financial_transaction_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_financial_transaction = db.scalars(
            select(FinancialTransaction).where(FinancialTransaction.id == financial_transaction_id)).first()
        if db_financial_transaction:
            db.delete(db_financial_transaction)
            db.commit()
            return {"massage": f"financial transaction with id: {financial_transaction_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="financial transaction not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
