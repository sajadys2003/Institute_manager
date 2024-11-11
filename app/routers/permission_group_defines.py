from app.models import PermissionGroupDefine
from app.schemas import PermissionGroupDefineIn, PermissionGroupDefineUpdate, PermissionGroupDefineResponse

# common modules
from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from sqlalchemy import and_
from app.dependencies import SessionDep, PageDep
from datetime import datetime

router = APIRouter(prefix="/permission_group_defines")


async def get_by_id(db: SessionDep, permission_group_define_id: int) -> PermissionGroupDefine:
    criteria = PermissionGroupDefine.id == permission_group_define_id
    stored_record = db.query(PermissionGroupDefine).where(criteria).scalar()
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PermissionGroupDefineResponse])
async def get_all_permission_group_defines(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_records = db.query(PermissionGroupDefine).offset(page.offset).limit(page.limit)
        return stored_records.all()


@router.get(path="/{permission_group_define_id}", response_model=PermissionGroupDefineResponse)
async def get_permission_group_define_by_id(
        db: SessionDep,
        permission_group_define_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_group_define_id)
        return stored_record


@router.post(path="/", response_model=PermissionGroupDefineResponse, status_code=status.HTTP_201_CREATED)
async def create_permission_group_define(
        db: SessionDep,
        data: PermissionGroupDefineIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        criteria = and_(
            PermissionGroupDefine.permission_group_id == data.permission_group_id,
            PermissionGroupDefine.permission_id == data.permission_id
        )
        found = db.query(PermissionGroupDefine).where(criteria).scalar()
        if found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="already exists")

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        new_record = PermissionGroupDefine(**data_dict)
        db.add(new_record)
        db.commit()
        return new_record


@router.put(path="/{permission_group_define_id}", response_model=PermissionGroupDefineResponse)
async def update_permission_group_define(
        db: SessionDep,
        permission_group_define_id: int,
        data: PermissionGroupDefineUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        criteria = and_(
            PermissionGroupDefine.permission_group_id == data.permission_group_id,
            PermissionGroupDefine.permission_id == data.permission_id,
            PermissionGroupDefine.id != permission_group_define_id
        )
        found = db.query(PermissionGroupDefine).where(criteria).scalar()
        if found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="already exists")

        stored_record = await get_by_id(db, permission_group_define_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})

        for key, value in data_dict.items():
            setattr(stored_record, key, value)
        db.commit()

        return stored_record


@router.delete(path="/{permission_group_define_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group_define(
        db: SessionDep,
        permission_group_define_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_group_define_id)
        db.delete(stored_record)
        db.commit()
