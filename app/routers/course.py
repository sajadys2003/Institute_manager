from fastapi import Depends, HTTPException
from app.models import Course
from app.schemas import CourseIn, CourseResponse, CourseUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_, or_
from app.routers.security import CurrentUser

router = APIRouter()


# Endpoints of course
# add all Endpoints for course
# -------------------------------------------------------------------------------------------------------


@router.post("/course/create", tags=["course"], response_model=CourseResponse)
async def create_course(user_auth: CurrentUser, course: CourseIn, db: Session = Depends(get_session)):
    if user_auth:
        course_dict = course.dict()
        course_dict["record_date"] = datetime.now()
        course_dict["recorder_id"] = user_auth.id
        db_course = Course(**course_dict)
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course", tags=["course"], response_model=list[CourseResponse])
async def get_courses(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth:
        if search:
            criteria = and_(Course.is_enabled, or_(Course.name.contains(search)))
            courses = db.scalars(select(Course).where(criteria).limit(pagination.limit).offset(pagination.offset))
            if courses:
                return courses
            raise HTTPException(status_code=404, detail="course not found!")
        courses = db.scalars(select(Course).limit(pagination.limit).offset(pagination.offset))
        if courses:
            return courses
        raise HTTPException(status_code=404, detail="course not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course/{course_id}", tags=["course"], response_model=CourseResponse)
async def get_course(user_auth: CurrentUser, course_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_course = db.scalars(select(Course).where(Course.id == course_id).where(Course.is_enabled)).first()
        if db_course:
            return db_course
        raise HTTPException(status_code=404, detail="course not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/course/update/{course_id}", tags=["course"], response_model=CourseResponse)
async def update_course(
        user_auth: CurrentUser,
        course: CourseUpdate,
        course_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:
        db_course = db.scalars(select(Course).where(Course.id == course_id).where(Course.is_enabled)).first()
        if db_course is None:
            raise HTTPException(status_code=404, detail="course not found!")
        course_dict = course.model_dump(exclude_unset=True)
        course_dict["record_date"] = datetime.now()
        course_dict["recorder_id"] = user_auth.id
        for key, value in course_dict.items():
            setattr(db_course, key, value)
        db.commit()
        return db_course
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/course/delete/{course_id}", tags=["course"])
async def delete_course(user_auth: CurrentUser, course_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_course = db.scalars(select(Course).where(Course.id == course_id).where(Course.is_enabled)).first()
        if db_course:
            db_course.is_enabled = False
            db.commit()
            return {"massage": f"course with id: {course_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="course not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
