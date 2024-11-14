from inspect import currentframe
from fastapi import Depends, HTTPException
from app.models import CoursePrice
from app.schemas import CoursePriceIn, CoursePriceResponse, CoursePriceUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of course price
# add all Endpoints for course price
# -------------------------------------------------------------------------------------------------------


@router.post("/course_price/create", tags=["course_price"], response_model=CoursePriceResponse)
async def create_course_price(user_auth: CurrentUser, course_price: CoursePriceIn, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
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
            raise HTTPException(status_code=400, detail=f"integrity error adding course price {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding course price {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course_price", tags=["course_price"], response_model=list[CoursePriceResponse])
async def get_course_prices(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), course_id: int | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        if course_id:
            course_prices = db.scalars(
                select(CoursePrice).where(
                    CoursePrice.course_id == course_id).limit(pagination.limit).offset(pagination.offset))
            return course_prices
        course_prices = db.scalars(select(CoursePrice).limit(pagination.limit).offset(pagination.offset))
        if course_prices:
            return course_prices
        raise HTTPException(status_code=404, detail="course price not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course_price/{course_price_id}", tags=["course_price"], response_model=CoursePriceResponse)
async def get_course_price(user_auth: CurrentUser, course_price_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
        if db_course_price:
            return db_course_price
        raise HTTPException(status_code=404, detail="course price not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/course_price/update/{course_price_id}", tags=["course_price"], response_model=CoursePriceResponse)
async def update_course_price(
        user_auth: CurrentUser,
        course_price: CoursePriceUpdate,
        course_price_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
            if db_course_price is None:
                raise HTTPException(status_code=404, detail="course price not found!")
            course_price_dict = course_price.model_dump(exclude_unset=True)
            course_price_dict["record_date"] = datetime.now()
            course_price_dict["recorder_id"] = user_auth.id
            for key, value in course_price_dict.items():
                setattr(db_course_price, key, value)
            db.commit()
            return db_course_price
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating course price {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating course price {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/course_price/delete/{course_price_id}", tags=["course_price"])
async def delete_course_price(user_auth: CurrentUser, course_price_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
        if db_course_price:
            db.delete(db_course_price)
            db.commit()
            return {"massage": f"course price with id: {course_price_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="course price not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
