from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import Course
from app.schemas import CourseIn, CourseResponse, CourseUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/courses")


# Endpoints of course
# add all Endpoints for course
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["courses"], response_model=CourseResponse)
async def create_course(user_auth: CurrentUser, course: CourseIn, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            course_dict = course.model_dump()
            course_dict["record_date"] = datetime.now()
            course_dict["recorder_id"] = user_auth.id
            db_course = Course(**course_dict)
            db.add(db_course)
            db.commit()
            db.refresh(db_course)
            return db_course
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["courses"], response_model=list[CourseResponse])
async def get_courses(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), name: str | None = None,
        lesson_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            Course.name.contains(name)
            if name else True,
            Course.lesson_id == lesson_id
            if (lesson_id or lesson_id == 0) else True
        )
        return db.scalars(select(Course).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{course_id}", tags=["courses"], response_model=CourseResponse)
async def get_course_by_id(user_auth: CurrentUser, course_id: int, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
        if db_course:
            return db_course
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course not found!")


@router.put("/{course_id}", tags=["courses"], response_model=CourseResponse)
async def update_course(
        user_auth: CurrentUser,
        course: CourseUpdate,
        course_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
            if db_course is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course not found!")
            course_dict = course.model_dump(exclude_unset=True)
            course_dict["record_date"] = datetime.now()
            course_dict["recorder_id"] = user_auth.id
            for key, value in course_dict.items():
                setattr(db_course, key, value)
            db.commit()
            return db_course
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{course_id}", tags=["courses"])
async def delete_course(user_auth: CurrentUser, course_id: int, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
            if db_course:
                db.delete(db_course)
                db.commit()
                return {"massage": f"course with id: {course_id} successfully deleted"}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")
