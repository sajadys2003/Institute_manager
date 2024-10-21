from src.models import PermissionGroup
from src.schemas import PermissionGroupIn
from src.schemas import PermissionGroupUpdate
from src.schemas import PermissionGroupOut

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
class PermissionGroupCrud:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        criteria = PermissionGroup.is_enabled.is_(True)
        stored_records = self.session.query(PermissionGroup).where(criteria)
        return stored_records.all()

    def get_by_id(self, permission_group_id):
        criteria = and_(
            PermissionGroup.id == permission_group_id,
            PermissionGroup.is_enabled.is_(True)
        )
        stored_record = self.session.query(PermissionGroup).where(criteria)
        return stored_record.scalar()

    def get_by_name(self, name: str):
        criteria = and_(
            PermissionGroup.name.like(name.strip()),
            PermissionGroup.is_enabled.is_(True)
        )
        stored_record = self.session.query(PermissionGroup).where(criteria)
        return stored_record.scalar()

    def create(self, data: PermissionGroupIn):
        if self.is_unique_to_create(data.name):
            data_dict = data.dict()
            data_dict["record_date"] = datetime.now()
            new_record = PermissionGroup(**data_dict)

            self.session.add(new_record)
            self.session.commit()
            return new_record

    def update(self, stored_record: PermissionGroup, data: PermissionGroupUpdate):

        if self.is_unique_to_update(data.name, stored_record.id):

            data_dict = data.model_dump(exclude_unset=True)
            data_dict["record_date"] = datetime.now()  # update record_date

            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            self.session.commit()

            updated_record = stored_record
            return updated_record

    def delete(self, stored_record: PermissionGroup):
        stored_record.is_enabled = False
        self.session.commit()

    """
    'name' fields in permission_groups table must be unique. 
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

    def is_unique_to_update(self, name: str, permission_group_id: int):
        stored_record = self.get_by_name(name)
        if stored_record and (stored_record.id != permission_group_id):

            raise HTTPException(status_code=409,
                                detail="record already exists")
        else:
            return True


router = APIRouter(prefix="/permission_groups")


@router.get(path="/", response_model=list[PermissionGroupOut])
async def get_all(
        session: Annotated[Session, Depends(get_session)]
):
    crud = PermissionGroupCrud(session)

    stored_records = crud.get_all()
    return stored_records


@router.get(path="/{permission_group_id}", response_model=PermissionGroupOut)
async def get_by_id(
        session: Annotated[Session, Depends(get_session)],
        permission_group_id: int
):
    crud = PermissionGroupCrud(session)

    stored_record = crud.get_by_id(permission_group_id)

    if stored_record:
        return stored_record
    else:
        raise HTTPException(status_code=404,
                            detail="record not found")


@router.post(path="/", response_model=PermissionGroupOut, status_code=HTTPStatus.CREATED)
async def create(
        session: Annotated[Session, Depends(get_session)],
        data: PermissionGroupIn
):
    crud = PermissionGroupCrud(session)

    try:
        stored_new_record = crud.create(data)
        return stored_new_record

    except IntegrityError:
        raise HTTPException(status_code=422,
                            detail="unable to process the request due to integrity error")


@router.put(path="/{permission_group_id}", response_model=PermissionGroupOut)
async def update(
        session: Annotated[Session, Depends(get_session)],
        permission_group_id: int,
        data: PermissionGroupUpdate
):
    crud = PermissionGroupCrud(session)

    stored_record = crud.get_by_id(permission_group_id)

    if stored_record:

        stored_updated_record = crud.update(stored_record, data)
        return stored_updated_record

    else:
        raise HTTPException(status_code=404,
                            detail="record not found")


@router.delete(path="/{permission_group_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete(
        session: Annotated[Session, Depends(get_session)],
        permission_group_id: int
):
    crud = PermissionGroupCrud(session)

    stored_record = crud.get_by_id(permission_group_id)

    if stored_record:
        crud.delete(stored_record)
    else:
        raise HTTPException(status_code=404,
                            detail="record not found")
