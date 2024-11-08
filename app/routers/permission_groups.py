from app.models import PermissionGroup
from app.schemas import PermissionGroupIn, PermissionGroupUpdate, PermissionGroupResponse

# common modules
from fastapi import APIRouter
from fastapi import HTTPException, status
from sqlalchemy import and_
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime

router = APIRouter(prefix="/permissions")


@router.get("/", response_model=list[PermissionGroupResponse])
async def get_all_permission_groups(
        db: SessionDep,
        commons: CommonsDep
):
    if commons.q:
        criteria = and_(
            PermissionGroup.is_enabled,
            PermissionGroup.name.contains(commons.q)
        )
    else:
        criteria = PermissionGroup.is_enabled

    stored_records = db.query(PermissionGroup).where(criteria).offset(commons.offset).limit(commons.limit)
    return stored_records.all()


@router.get(path="/{permission_group_id}", response_model=PermissionGroupResponse)
async def get_permission_group_by_id(
        db: SessionDep,
        permission_id: int
):
    criteria = and_(
        PermissionGroup.id == permission_id,
        PermissionGroup.is_enabled
    )
    stored_record = db.query(PermissionGroup).where(criteria).scalar()

    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.post(path="/", response_model=PermissionGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_permission_group(
        db: SessionDep,
        data: PermissionGroupIn
):
    data_dict = data.model_dump()
    data_dict.update({"recorder_id": 1, "record_date": datetime.now()})
    new_record = PermissionGroup(**data_dict)
    db.add(new_record)
    db.commit()
    return new_record


@router.put(path="/{permission_group_id}", response_model=PermissionGroupResponse)
async def update_permission(
        db: SessionDep,
        permission_group_id: int,
        data: PermissionGroupUpdate,
):
    stored_record = await get_permission_group_by_id(db, permission_group_id)

    data_dict = data.model_dump(exclude_unset=True)
    data_dict.update({"recorder_id": 1, "record_date": datetime.now()})

    for key, value in data_dict.items():
        setattr(stored_record, key, value)
    db.commit()

    return stored_record


@router.delete(path="/{permission_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group(
        db: SessionDep,
        permission_group_id: int,
):
    stored_record = await get_permission_group_by_id(db, permission_group_id)
    stored_record.is_enabled = False
    db.commit()
