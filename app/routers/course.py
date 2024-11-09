from fastapi import Depends, HTTPException
from app.models import Course
from app.schemas import Course, CourseResponse, CourseUpdate
from app.dependencies import get_session, CommonsDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_
from app.routers.authentication import AuthorizedUser

router = APIRouter()


# Endpoints of course
# add all Endpoints for course
# -------------------------------------------------------------------------------------------------------


@router.post("/course/create", tags=["course"], response_model=CourseResponse)
async def create_course(user_auth: AuthorizedUser, course: Course, db: Session = Depends(get_session)):

    if user_auth:
        course_dict = course.dict()
        course_dict["record_date"] = datetime.now()
        course_dict["recorder_id"] = user_auth.id
        db_course = Course(**course_dict)
        db.add(db_course)
        db.commit()
        db.refresh(db_course)

        return db_course


@router.get("/course", tags=["course"], response_model=list[CourseResponse])
async def get_courses(user_auth: AuthorizedUser, db: Session = Depends(get_session), params=CommonsDep):
    if user_auth:

        if params.q:
            criteria = and_(Course.is_enabled, Course.name.contains(params.q))

            return db.scalars(select(Course).where(criteria).limit(params.size).offset(params.page))

        return db.scalars(select(Course).limit(params.size).offset(params.page))


@router.get("/course/{course_id}", tags=["course"], response_model=CourseResponse)
async def get_course(user_auth: AuthorizedUser, course_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
        if db_course:
            return db_course
        raise HTTPException(status_code=404, detail="course not found!")


@router.put("/course/update/{course_id}", tags=["course"], response_model=CourseResponse)
async def update_course(
        user_auth: AuthorizedUser,
        course: CourseUpdate,
        course_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:

        db_course = db.scalars(select(Course).where(Course.id == course_id)).first()

        if db_course is None:
            raise HTTPException(status_code=404, detail="course not found!")

        course_dict = course.model_dump(exclude_unset=True)
        course_dict["record_date"] = datetime.now()
        course_dict["recorder_id"] = user_auth.id

        for key, value in course:
            setattr(db_course, key, value)

        db.commit()

        return db_course


@router.delete("/course/delete/{course_id}", tags=["course"])
async def delete_course(user_auth: AuthorizedUser, course_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
        if db_course:
            db_course.is_enabled = False
            db.commit()
            return {"massage": f"course with id: {course_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="course not found!")
