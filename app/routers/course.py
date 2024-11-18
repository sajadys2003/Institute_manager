from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter
from app.models import Course
from app.schemas import CourseIn, CourseOut, CourseUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of course
# add all Endpoints for course
# -------------------------------------------------------------------------------------------------------


@router.post("/course/create", tags=["course"], response_model=CourseOut)
async def create_course(user_auth: CurrentUser, course: CourseIn, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
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
            raise HTTPException(status_code=400, detail=f"integrity error adding course {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding course {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course", tags=["course"], response_model=list[CourseOut])
async def get_courses(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), name: str | None = None,
        lesson_id: int | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(
            Course.name.contains(name)
            if name else True,
            Course.lesson_id == lesson_id
            if (lesson_id or lesson_id == 0) else True
        )
        return db.scalars(select(Course).where(criteria).limit(pagination.limit).offset(pagination.offset))
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course/{course_id}", tags=["course"], response_model=CourseOut)
async def get_course(user_auth: CurrentUser, course_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
        if db_course:
            return db_course
        raise HTTPException(status_code=404, detail="course not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/course/update/{course_id}", tags=["course"], response_model=CourseOut)
async def update_course(
        user_auth: CurrentUser,
        course: CourseUpdate,
        course_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
            if db_course is None:
                raise HTTPException(status_code=404, detail="course not found!")
            course_dict = course.model_dump(exclude_unset=True)
            course_dict["record_date"] = datetime.now()
            course_dict["recorder_id"] = user_auth.id
            for key, value in course_dict.items():
                setattr(db_course, key, value)
            db.commit()
            return db_course
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating course {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating course {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/course/delete/{course_id}", tags=["course"])
async def delete_course(user_auth: CurrentUser, course_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_course = db.scalars(select(Course).where(Course.id == course_id)).first()
            if db_course:
                db.delete(db_course)
                db.commit()
                return {"massage": f"course with id: {course_id} successfully deleted"}
            else:
                raise HTTPException(status_code=404, detail="course not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error deleting course {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error deleting course {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")
