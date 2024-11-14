from app.models import Role
from app.schemas import RoleIn, RoleUpdate, RoleResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/roles")


async def get_by_id(db: SessionDep, role_id: int) -> Role:
    stored_record = db.get(Role, role_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[RoleResponse])
async def get_all_roles(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = Role.name.contains(q)
            stored_records = db.query(Role).where(criteria)

        else:
            stored_records = db.query(Role)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{role_id}", response_model=RoleResponse)
async def get_role_by_id(
        db: SessionDep,
        role_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, role_id)
        return stored_record


@router.post(path="/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
        db: SessionDep,
        data: RoleIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Role(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{role_id}", response_model=RoleResponse)
async def update_role(
        db: SessionDep,
        role_id: int,
        data: RoleUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, role_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
        db: SessionDep,
        role_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, role_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
