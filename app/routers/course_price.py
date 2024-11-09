from fastapi import Depends, HTTPException
from app.models import CoursePrice
from app.schemas import CoursePrice, CoursePriceResponse, CoursePriceUpdate
from app.dependencies import get_session, CommonsDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_, or_
from app.routers.authentication import AuthorizedUser

router = APIRouter()


# Endpoints of course price
# add all Endpoints for course price
# -------------------------------------------------------------------------------------------------------


@router.post("/course_price/create", tags=["course_price"], response_model=CoursePriceResponse)
async def create_course_price(user_auth: AuthorizedUser, course_price: CoursePrice, db: Session = Depends(get_session)):

    if user_auth:
        course_price_dict = course_price.dict()
        course_price_dict["record_date"] = datetime.now()
        course_price_dict["recorder_id"] = user_auth.id
        db_course_price = CoursePrice(**course_price_dict)
        db.add(db_course_price)
        db.commit()
        db.refresh(db_course_price)

        return db_course_price


@router.get("/course_price", tags=["course_price"], response_model=list[CoursePriceResponse])
async def get_course_prices(user_auth: AuthorizedUser, db: Session = Depends(get_session), params=CommonsDep):
    if user_auth:

        if params.q:
            criteria = and_(CoursePrice.is_enabled,
                            or_(CoursePrice.name.contains(params.q),
                                CoursePrice.course_id.contains(int(params.q))))

            return db.scalars(select(CoursePrice).where(criteria).limit(params.size).offset(params.page))

        return db.scalars(select(CoursePrice).limit(params.size).offset(params.page))


@router.get("/course_price/{course_price_id}", tags=["course_price"], response_model=CoursePriceResponse)
async def get_course_price(user_auth: AuthorizedUser, course_price_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
        if db_course_price:
            return db_course_price
        raise HTTPException(status_code=404, detail="course price not found!")


@router.put("/course_price/update/{course_price_id}", tags=["course_price"], response_model=CoursePriceResponse)
async def update_course_price(
        user_auth: AuthorizedUser,
        course_price: CoursePriceUpdate,
        course_price_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:

        db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()

        if db_course_price is None:
            raise HTTPException(status_code=404, detail="course price not found!")

        course_price_dict = course_price.model_dump(exclude_unset=True)
        course_price_dict["record_date"] = datetime.now()
        course_price_dict["recorder_id"] = user_auth.id

        for key, value in course_price:
            setattr(db_course_price, key, value)

        db.commit()

        return db_course_price


@router.delete("/course_price/delete/{course_price_id}", tags=["course_price"])
async def delete_course_price(user_auth: AuthorizedUser, course_price_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_course_price = db.scalars(select(CoursePrice).where(CoursePrice.id == course_price_id)).first()
        if db_course_price:
            db_course_price.is_enabled = False
            db.commit()
            return {"massage": f"course price with id: {course_price_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="course price not found!")
