from app.models import PermissionGroupDefine
from app.schemas import PermissionGroupDefineIn, PermissionGroupDefineUpdate, PermissionGroupDefineResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

router = APIRouter(prefix="/permission_group_defines")


async def get_by_id(db: SessionDep, permission_group_id: int, permission_id: int) -> PermissionGroupDefine:
    stored_record = db.get(PermissionGroupDefine, [permission_group_id, permission_id])
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PermissionGroupDefineResponse])
async def get_permission_group_defines(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        permission_group_id: int | None = None,
        permission_id: int | None = None,
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        criteria = and_(
            PermissionGroupDefine.permission_group_id == permission_group_id
            if (permission_group_id or permission_group_id == 0) else True,

            PermissionGroupDefine.permission_id == permission_id
            if (permission_id or permission_id == 0) else True
        )
        stored_records = db.query(PermissionGroupDefine).where(criteria)
        return stored_records.offset(page.offset).limit(page.limit).all()


@router.post(path="/", response_model=PermissionGroupDefineResponse, status_code=status.HTTP_201_CREATED)
async def create_permission_group_define(
        db: SessionDep,
        data: PermissionGroupDefineIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = PermissionGroupDefine(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/", response_model=PermissionGroupDefineResponse)
async def update_permission_group_define(
        db: SessionDep,
        permission_group_define_id: int,
        permission_id: int,
        data: PermissionGroupDefineUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, permission_group_define_id, permission_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group_define(
        db: SessionDep,
        permission_group_define_id: int,
        permission_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_group_define_id, permission_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
