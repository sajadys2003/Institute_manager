from src.models import Role
from src.schemas import RoleIn
from src.schemas import RoleUpdate
from src.schemas import RoleOut

# common imported modules among all files in 'src.routers'
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import Session
from src.initdb import get_session
from typing import Annotated
from http import HTTPStatus
from datetime import datetime


# define a Crud class to interact with the database
class RoleCrud:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        criteria = Role.is_enabled.is_(True)
        stored_records = self.session.query(Role).where(criteria)
        return stored_records.all()

    def get_by_id(self, role_id):
        criteria = and_(
            Role.id == role_id,
            Role.is_enabled.is_(True)
        )
        stored_record = self.session.query(Role).where(criteria)
        return stored_record.scalar()

    def get_by_name(self, name: str) -> Role:
        criteria = and_(
            Role.name.like(name.strip()),
            Role.is_enabled.is_(True)
        )
        stored_record = self.session.query(Role).where(criteria)
        return stored_record.scalar()

    def create(self, data: RoleIn):
        if self.is_unique_to_create(data.name):
            data_dict = data.dict()
            data_dict["record_date"] = datetime.now()
            new_record = Role(**data_dict)

            self.session.add(new_record)
            self.session.commit()
            return new_record

    def update(self, stored_record: Role, data: RoleUpdate):

        if self.is_unique_to_update(data.name, stored_record.id):

            data_dict = data.model_dump(exclude_unset=True)
            data_dict["record_date"] = datetime.now()  # update record_date

            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            self.session.commit()

            updated_record = stored_record
            return updated_record

    def delete(self, stored_record: Role):
        stored_record.is_enabled = False
        self.session.commit()

    """
    'name' fields in roles table must be unique. 
    The following methods return True if input name is unique.
    Notice we dont include name of records where 'is_enabled == False'
    """

    def is_unique_to_create(self, name: str):
        stored_record = self.get_by_name(name)
        if stored_record:

            raise HTTPException(status_code=409,
                                detail="record already exists")
        else:
            return True

    def is_unique_to_update(self, name: str, role_id: int):
        stored_record = self.get_by_name(name)

        if stored_record and (stored_record.id != role_id):

            raise HTTPException(status_code=409,
                                detail="record already exists")
        else:
            return True


router = APIRouter(prefix="/roles")


@router.get(path="/", response_model=list[RoleOut])
async def get_all(
        session: Annotated[Session, Depends(get_session)]
):
    crud = RoleCrud(session)

    stored_records = crud.get_all()
    return stored_records


@router.get(path="/{role_id}", response_model=RoleOut)
async def get_by_id(
        session: Annotated[Session, Depends(get_session)],
        role_id: int
):
    crud = RoleCrud(session)

    stored_record = crud.get_by_id(role_id)

    if stored_record:
        return stored_record
    else:
        raise HTTPException(status_code=404,
                            detail="record not found")


@router.post(path="/", response_model=RoleOut, status_code=HTTPStatus.CREATED)
async def create(
        session: Annotated[Session, Depends(get_session)],
        data: RoleIn
):
    crud = RoleCrud(session)

    try:
        stored_new_record = crud.create(data)
        return stored_new_record

    except IntegrityError:
        raise HTTPException(status_code=422,
                            detail="unable to process the request due to integrity error")


@router.put(path="/{role_id}", response_model=RoleOut)
async def update(
        session: Annotated[Session, Depends(get_session)],
        role_id: int,
        data: RoleUpdate
):
    crud = RoleCrud(session)

    stored_record = crud.get_by_id(role_id)

    if stored_record:

        stored_updated_record = crud.update(stored_record, data)
        return stored_updated_record

    else:
        raise HTTPException(status_code=404,
                            detail="record not found")


@router.delete(path="/{role_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete(
        session: Annotated[Session, Depends(get_session)],
        role_id: int
):
    crud = RoleCrud(session)

    stored_record = crud.get_by_id(role_id)

    if stored_record:
        crud.delete(stored_record)
    else:
        raise HTTPException(status_code=404,
                            detail="record not found")
