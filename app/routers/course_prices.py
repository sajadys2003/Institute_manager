from app.models import CoursePrice
from app.schemas import CoursePriceIn, CoursePriceUpdate, CoursePriceResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/course_prices")


async def get_by_id(db: SessionDep, course_price_id: int) -> CoursePrice:
    stored_record = db.get(CoursePrice, course_price_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[CoursePriceResponse])
async def get_all_course_prices(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        course_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if course_id:
            criteria = CoursePrice.course_id == course_id
            stored_records = db.query(CoursePrice).where(criteria)

        else:
            stored_records = db.query(CoursePrice)
        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{course_price_id}", response_model=CoursePriceResponse)
async def get_course_price_by_id(
        db: SessionDep,
        course_price_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, course_price_id)
        return stored_record


@router.post(path="/", response_model=CoursePriceResponse, status_code=status.HTTP_201_CREATED)
async def create_course_price(
        db: SessionDep,
        data: CoursePriceIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if not data.date:
            data.date = datetime.now()

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = CoursePrice(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{course_price_id}", response_model=CoursePriceResponse)
async def update_course_price(
        db: SessionDep,
        course_price_id: int,
        data: CoursePriceUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, course_price_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{course_price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_price(
        db: SessionDep,
        course_price_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, course_price_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
