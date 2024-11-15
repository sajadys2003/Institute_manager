from app.models import Building
from app.schemas import BuildingIn, BuildingUpdate, BuildingResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, CommonsDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/buildings")


async def get_by_id(db: SessionDep, building_id: int) -> Building:
    stored_record = db.get(Building, building_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[BuildingResponse])
async def get_all_buildings(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = Building.name.ilike(q)
            stored_records = db.query(Building).where(criteria)

        else:
            stored_records = db.query(Building)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{building_id}", response_model=BuildingResponse)
async def get_building_by_id(
        db: SessionDep,
        building_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, building_id)
        return stored_record


@router.post(path="/", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
async def create_building(
        db: SessionDep,
        data: BuildingIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Building(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{building_id}", response_model=BuildingResponse)
async def update_building(
        db: SessionDep,
        building_id: int,
        data: BuildingUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, building_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
        db: SessionDep,
        building_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, building_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
