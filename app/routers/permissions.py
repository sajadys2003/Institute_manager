from app.models import Permission
from app.schemas import PermissionIn, PermissionUpdate, PermissionResponse

# common modules
from fastapi import APIRouter
from fastapi import HTTPException, status
from sqlalchemy import and_
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime

router = APIRouter(prefix="/permissions")


@router.get("/", response_model=list[PermissionResponse])
async def get_all(
        db: SessionDep,
        commons: CommonsDep
):
    if commons.q:
        criteria = and_(
            Permission.is_enabled,
            Permission.name.contains(commons.q)
        )
    else:
        criteria = Permission.is_enabled

    stored_records = db.query(Permission).where(criteria).offset(commons.offset).limit(commons.limit).all()
    return stored_records


@router.get(path="/{permission_id}", response_model=PermissionResponse)
async def get_by_id(
        db: SessionDep,
        permission_id: int
):
    criteria = and_(
        Permission.id == permission_id,
        Permission.is_enabled
    )
    stored_record = db.query(Permission).where(criteria).scalar()

    if not stored_record:
        HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.post(path="/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create(
        db: SessionDep,
        data: PermissionIn
):
    if not db.get(Permission, data.parent_id):
        raise HTTPException
    data_dict = data.model_dump()
    data_dict.update({"recorder_id": 1, "record_date": datetime.now()})
    new_record = Permission(**data_dict)
    db.add(new_record)
    db.commit()
    return new_record


@router.put(path="/{permission_id}", response_model=PermissionResponse)
async def update(
        db: SessionDep,
        permission_id: int,
        data: PermissionUpdate,
):
    criteria = and_(
        Permission.id == permission_id,
        Permission.is_enabled
    )
    stored_record = db.query(Permission).where(criteria).scalar()
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")

    if parent_id := data.parent_id:
        if not db.get(Permission, parent_id):
            raise HTTPException()

    data_dict = data.model_dump(exclude_unset=True)
    data_dict.update({"recorder_id": 1, "record_date": datetime.now()})

    for key, value in data_dict.items():
        setattr(stored_record, key, value)
    db.commit()

    return stored_record


@router.delete(path="/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        db: SessionDep,
        permission_id: int,
):
    criteria = and_(
        Permission.id == permission_id,
        Permission.is_enabled
    )
    stored_record = db.query(Permission).where(criteria).scalar()
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    stored_record.is_enabled = False
    db.commit()