from app.models import Permission
from app.schemas import PermissionIn, PermissionUpdate, PermissionResponse

# common modules
from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from sqlalchemy import and_
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime

router = APIRouter(prefix="/permissions")


async def get_by_id(db: SessionDep, permission_id: int) -> Permission:
    criteria = and_(
        Permission.id == permission_id,
        Permission.is_enabled
    )
    stored_record = db.query(Permission).where(criteria).scalar()

    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PermissionResponse])
async def get_all_permissions(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = and_(
                Permission.is_enabled,
                Permission.name.contains(q)
            )
        else:
            criteria = Permission.is_enabled

        stored_records = db.query(Permission).where(criteria).offset(commons.offset).limit(commons.limit)
        return stored_records.all()


@router.get(path="/{permission_id}", response_model=PermissionResponse)
async def get_permission_by_id(
        db: SessionDep,
        permission_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_id)
        return stored_record


@router.post(path="/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
        db: SessionDep,
        data: PermissionIn,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        new_record = Permission(**data_dict)
        db.add(new_record)
        db.commit()
        return new_record


@router.put(path="/{permission_id}", response_model=PermissionResponse)
async def update_permission(
        db: SessionDep,
        permission_id: int,
        data: PermissionUpdate,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, permission_id)

        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})

        for key, value in data_dict.items():
            setattr(stored_record, key, value)
        db.commit()

        return stored_record


@router.delete(path="/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
        db: SessionDep,
        permission_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_id)
        stored_record.is_enabled = False
        db.commit()
