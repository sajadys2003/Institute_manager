from app.models import FinancialTransaction
from app.schemas import FinancialTransactionIn, FinancialTransactionUpdate, FinancialTransactionResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/financial_transactions")


async def get_by_id(db: SessionDep, financial_transaction_id: int) -> FinancialTransaction:
    stored_record = db.get(FinancialTransaction, financial_transaction_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[FinancialTransactionResponse])
async def get_all_financial_transactions(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        user_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = FinancialTransaction.user_id == user_id if (user_id or user_id == 0) else True
        stored_records = db.query(FinancialTransaction).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{financial_transaction_id}", response_model=FinancialTransactionResponse)
async def get_financial_transaction_by_id(
        db: SessionDep,
        financial_transaction_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, financial_transaction_id)
        return stored_record


@router.post(path="/", response_model=FinancialTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_financial_transaction(
        db: SessionDep,
        data: FinancialTransactionIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if not data.transaction_date:
            data.transaction_date = datetime.now()

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = FinancialTransaction(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{financial_transaction_id}", response_model=FinancialTransactionResponse)
async def update_financial_transaction(
        db: SessionDep,
        financial_transaction_id: int,
        data: FinancialTransactionUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, financial_transaction_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{financial_transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_financial_transaction(
        db: SessionDep,
        financial_transaction_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, financial_transaction_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
