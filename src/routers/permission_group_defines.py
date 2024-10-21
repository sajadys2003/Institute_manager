from src.models import PermissionGroupDefine
from src.models import Permission
from src.models import PermissionGroup
from src.schemas import PermissionGroupDefineIn
from src.schemas import PermissionGroupDefineUpdate
from src.schemas import PermissionGroupDefineOut

from src.routers.permissions import PermissionCrud
from src.routers.permission_groups import PermissionGroupCrud

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
class PermissionGroupDefineCrud:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        stored_records = self.session.query(PermissionGroupDefine)
        return stored_records.all()

    def get_by_id(self, permission_group_define_id):
        criteria = PermissionGroupDefine.id == permission_group_define_id
        stored_record = self.session.query(PermissionGroupDefine).where(criteria)
        return stored_record.scalar()

    def get_by_content(self, permission_id, permission_group_id):
        criteria = and_(
            PermissionGroupDefine.permission_id == permission_id,
            PermissionGroupDefine.permission_group_id == permission_group_id
        )
        stored_record = self.session.query(PermissionGroupDefine).where(criteria)
        return stored_record.scalar()

    def create(self, data: PermissionGroupDefineIn):
        if self.is_unique_to_create(
                data.permission_id,
                data.permission_group_id
        ) and self.is_match(data.permission_group_id, data.permission_id):
            data_dict = data.dict()
            new_record = PermissionGroupDefine(**data_dict)

            self.session.add(new_record)
            self.session.commit()
            return new_record

    def update(self, stored_record: PermissionGroupDefine, data: PermissionGroupDefineUpdate):
        if self.is_unique_to_update(
                data.permission_id,
                data.permission_group_id,
                stored_record.id
        ) and self.is_match(data.permission_group_id, data.permission_id):

            data_dict = data.model_dump(exclude_unset=True)

            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            self.session.commit()

            updated_record = stored_record
            return updated_record

    def delete(self, stored_record: PermissionGroupDefine):
        self.session.delete(stored_record)
        self.session.commit()

    # returns True if permission_id & permission_group_id
    # match to a record in their respective tables
    def is_match(self, permission_group_id: int, permission_id: int):
        permission_record = PermissionCrud(self.session).get_by_id(permission_id)
        if permission_record:

            permission_group_record = PermissionGroupCrud(self.session).get_by_id(permission_group_id)
            if permission_group_record:

                return True

            else:
                raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                    detail="no permission_group_record matched permission_group_id={}"
                                    .format(permission_group_id))
        else:
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail="no permission_record matched permission_id={}"
                                .format(permission_id))

    """
        content of records in permission_group_defines table must be unique. 
        'content' = permission_id & permission_group_id
        The following methods return True if input content is unique.
        Notice we dont include name of records where 'is_enabled == False'
    """

    def is_unique_to_create(self, permission_id, permission_group_id):
        stored_record = self.get_by_content(permission_id, permission_group_id)
        if stored_record:

            raise HTTPException(status_code=409,
                                detail="record already exists")
        else:
            return True

    def is_unique_to_update(self, permission_id, permission_group_id, permission_group_define_id):
        stored_record = self.get_by_content(permission_id, permission_group_id)

        if stored_record and (stored_record.id != permission_group_define_id):

            raise HTTPException(status_code=409,
                                detail="record already exists")
        else:
            return True


# define a router
router = APIRouter(prefix="/permission_group_defines")


@router.get(path="/", response_model=list[PermissionGroupDefineOut])
async def get_all(
        session: Annotated[Session, Depends(get_session)]
):
    crud = PermissionGroupDefineCrud(session)

    stored_records = crud.get_all()
    return stored_records


@router.get(path="/{permission_group_define_id}", response_model=PermissionGroupDefineOut)
async def get_by_id(
        session: Annotated[Session, Depends(get_session)],
        permission_group_define_id: int
):
    crud = PermissionGroupDefineCrud(session)

    stored_record = crud.get_by_id(permission_group_define_id)

    if stored_record:
        return stored_record
    else:
        raise HTTPException(status_code=404,
                            detail="record not found")


@router.post(path="/", response_model=PermissionGroupDefineOut, status_code=HTTPStatus.CREATED)
async def create(
        session: Annotated[Session, Depends(get_session)],
        data: PermissionGroupDefineIn
):
    crud = PermissionGroupDefineCrud(session)

    try:
        stored_new_record = crud.create(data)
        return stored_new_record

    except IntegrityError:
        raise HTTPException(status_code=422,
                            detail="unable to process the request due to integrity error")


@router.put(path="/{permission_group_define_id}", response_model=PermissionGroupDefineOut)
async def update(
        session: Annotated[Session, Depends(get_session)],
        permission_group_define_id: int,
        data: PermissionGroupDefineUpdate
):
    crud = PermissionGroupDefineCrud(session)

    stored_record = crud.get_by_id(permission_group_define_id)

    if stored_record:

        stored_updated_record = crud.update(stored_record, data)
        return stored_updated_record

    else:
        raise HTTPException(status_code=404,
                            detail="record not found")


@router.delete(path="/{permission_group_define_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete(
        session: Annotated[Session, Depends(get_session)],
        permission_group_define_id: int
):
    crud = PermissionGroupDefineCrud(session)

    stored_record = crud.get_by_id(permission_group_define_id)

    if stored_record:
        crud.delete(stored_record)
    else:
        raise HTTPException(status_code=404,
                            detail="record not found")
