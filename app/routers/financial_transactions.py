from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import FinancialTransaction
from app.schemas import FinancialTransactionIn, FinancialTransactionResponse, FinancialTransactionUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/financial_transactions")


# Endpoints of financial transaction
# add all Endpoints for financial transaction
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["financial_transactions"], response_model=FinancialTransactionResponse)
async def create_financial_transaction(
        user_auth: CurrentUser, financial_transaction: FinancialTransactionIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            x = 0
            financial_transaction_dict = financial_transaction.model_dump()
            if financial_transaction_dict["presentation_id"]:
                x += 1
            if financial_transaction_dict["selected_presentation_id"]:
                x += 1
            if financial_transaction_dict["selected_exam_id"]:
                x += 1
            if x < 2:
                financial_transaction_dict["record_date"] = datetime.now()
                financial_transaction_dict["recorder_id"] = user_auth.id
                db_financial_transaction = FinancialTransaction(**financial_transaction_dict)
                db.add(db_financial_transaction)
                db.commit()
                db.refresh(db_financial_transaction)
                return db_financial_transaction
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="one of presentation_id , selected_presentation_id and selected_exam_id must enter")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["financial_transactions"], response_model=list[FinancialTransactionResponse])
async def get_financial_transactions(
        user_auth: CurrentUser,
        pagination: PageDep,
        db: Session = Depends(get_session),
        user_id: int | None = None,
        financial_category_id: int | None = None,
        presentation_id: int | None = None,
        selected_presentation_id: int | None = None,
        selected_exam_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            FinancialTransaction.user_id == user_id
            if (user_id or user_id == 0) else True,
            FinancialTransaction.financial_category_id == financial_category_id
            if (financial_category_id or financial_category_id == 0) else True,
            FinancialTransaction.presentation_id == presentation_id
            if (presentation_id or presentation_id == 0) else True,
            FinancialTransaction.selected_presentation_id == selected_presentation_id
            if (selected_presentation_id or selected_presentation_id == 0) else True,
            FinancialTransaction.selected_exam_id == selected_exam_id
            if (selected_exam_id or selected_exam_id == 0) else True
        )
        return db.scalars(select(FinancialTransaction).where(
            criteria).limit(pagination.limit).offset(pagination.offset))


@router.get(
    "/{financial_transaction_id}", tags=["financial_transactions"], response_model=FinancialTransactionResponse
)
async def get_financial_transaction_by_id(
        user_auth: CurrentUser, financial_transaction_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_financial_transaction = db.scalars(
            select(FinancialTransaction).where(FinancialTransaction.id == financial_transaction_id)).first()
        if db_financial_transaction:
            return db_financial_transaction
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="financial transaction not found!")


@router.put(
    "/{financial_transaction_id}", tags=["financial_transactions"], response_model=FinancialTransactionResponse
)
async def update_financial_transaction(
        user_auth: CurrentUser,
        financial_transaction: FinancialTransactionUpdate,
        financial_transaction_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_financial_transaction = db.scalars(
                select(FinancialTransaction).where(FinancialTransaction.id == financial_transaction_id)).first()
            if db_financial_transaction is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="financial transaction not found!")
            x = 0
            financial_transaction_dict = financial_transaction.model_dump(exclude_unset=True)
            if "presentation_id" in financial_transaction_dict.keys():
                if financial_transaction_dict["presentation_id"]:
                    x += 1
            if "selected_presentation_id" in financial_transaction_dict.keys():
                if financial_transaction_dict["selected_presentation_id"]:
                    x += 1
            if "selected_exam_id" in financial_transaction_dict:
                if financial_transaction_dict["selected_exam_id"]:
                    x += 1
            if x < 2:
                financial_transaction_dict["record_date"] = datetime.now()
                financial_transaction_dict["recorder_id"] = user_auth.id
                for key, value in financial_transaction_dict.items():
                    setattr(db_financial_transaction, key, value)
                db.commit()
                return db_financial_transaction
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="one of presentation_id , selected_presentation_id and selected_exam_id must enter")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{financial_transaction_id}", tags=["financial_transactions"])
async def delete_financial_transaction(
        user_auth: CurrentUser, financial_transaction_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_financial_transaction = db.scalars(
            select(FinancialTransaction).where(FinancialTransaction.id == financial_transaction_id)).first()
        if db_financial_transaction:
            db_financial_transaction.is_enabled = False
            db.commit()
            return {"massage": f"financial transaction with id: {financial_transaction_id} successfully deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="financial transaction not found!")
