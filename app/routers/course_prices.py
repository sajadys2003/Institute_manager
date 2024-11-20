from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import CoursePrice
from app.schemas import CoursePriceIn, CoursePriceResponse, CoursePriceUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/course_prices")


# Endpoints of course price
# add all Endpoints for course price
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["course_prices"], response_model=CoursePriceResponse)
async def create_course_price(
        user_auth: CurrentUser, course_price: CoursePriceIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            course_price_dict = course_price.dict()
            course_price_dict["record_date"] = datetime.now()
            course_price_dict["recorder_id"] = user_auth.id
            db_course_price = CoursePrice(**course_price_dict)
            db.add(db_course_price)
            db.commit()
            db.refresh(db_course_price)
            return db_course_price
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["course_prices"], response_model=list[CoursePriceResponse])
async def get_course_prices(
        user_auth: CurrentUser,
        pagination: PageDep,
        db: Session = Depends(get_session),
        course_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(CoursePrice.course_id == course_id
                        if (course_id or course_id == 0) else True,
                        CoursePrice.date >= from_date
                        if from_date else True,
                        CoursePrice.date <= to_date
                        if to_date else True)
        return db.scalars(select(CoursePrice).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{course_price_id}", tags=["course_prices"], response_model=CoursePriceResponse)
async def get_course_price_by_id(
        user_auth: CurrentUser, course_price_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
        if db_course_price:
            return db_course_price
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course price not found!")


@router.put("/{course_price_id}", tags=["course_prices"], response_model=CoursePriceResponse)
async def update_course_price(
        user_auth: CurrentUser,
        course_price: CoursePriceUpdate,
        course_price_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
            if db_course_price is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course price not found!")
            course_price_dict = course_price.model_dump(exclude_unset=True)
            course_price_dict["record_date"] = datetime.now()
            course_price_dict["recorder_id"] = user_auth.id
            for key, value in course_price_dict.items():
                setattr(db_course_price, key, value)
            db.commit()
            return db_course_price
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{course_price_id}", tags=["course_prices"])
async def delete_course_price(user_auth: CurrentUser, course_price_id: int, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
        if db_course_price:
            db.delete(db_course_price)
            db.commit()
            return {"massage": f"course price with id: {course_price_id} successfully deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course price not found!")
