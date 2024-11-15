from app.models import PermissionGroup
from app.schemas import PermissionGroupIn, PermissionGroupUpdate, PermissionGroupResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/permission_groups")


async def get_by_id(db: SessionDep, permission_group_id: int) -> PermissionGroup:
    stored_record = db.get(PermissionGroup, permission_group_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PermissionGroupResponse])
async def get_all_permission_groups(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = PermissionGroup.name.ilike(q)
            stored_records = db.query(PermissionGroup).where(criteria)

        else:
            stored_records = db.query(PermissionGroup)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{permission_group_id}", response_model=PermissionGroupResponse)
async def get_permission_group_by_id(
        db: SessionDep,
        permission_group_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_group_id)
        return stored_record

@router.post(path="/", response_model=PermissionGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_permission_group(
        db: SessionDep,
        data: PermissionGroupIn,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = PermissionGroup(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")



@router.put(path="/{permission_group_id}", response_model=PermissionGroupResponse)
async def update_permission_group(
        db: SessionDep,
        permission_group_id: int,
        data: PermissionGroupUpdate,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, permission_group_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{permission_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group(
        db: SessionDep,
        permission_group_id: int,
        current_user: CurrentUer

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_group_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")

