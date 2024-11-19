from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter
from app.models import CoursePrerequisite
from app.schemas import CoursePrerequisiteIn, CoursePrerequisiteOut, CoursePrerequisiteUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of course price
# add all Endpoints for course price
# -------------------------------------------------------------------------------------------------------


@router.post("/course_prerequisite/create", tags=["course_prerequisite"], response_model=CoursePrerequisiteOut)
async def create_course_prerequisite(
        user_auth: CurrentUser, course_prerequisite: CoursePrerequisiteIn, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            course_prerequisite_dict = course_prerequisite.model_dump()
            course_prerequisite_dict["record_date"] = datetime.now()
            course_prerequisite_dict["recorder_id"] = user_auth.id
            db_course_prerequisite = CoursePrerequisite(**course_prerequisite_dict)
            db.add(db_course_prerequisite)
            db.commit()
            db.refresh(db_course_prerequisite)
            return db_course_prerequisite
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error adding course prerequisite {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding course prerequisite {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course_prerequisite", tags=["course_prerequisite"], response_model=list[CoursePrerequisiteOut])
async def get_course_prerequisites(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session),
        main_course_id: int | None = None, prerequisite_id: int | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(
            CoursePrerequisite.main_course_id == main_course_id
            if (main_course_id or main_course_id == 0) else True,
            CoursePrerequisite.prerequisite_id == prerequisite_id
            if (prerequisite_id or prerequisite_id == 0) else True
        )
        return db.scalars(select(CoursePrerequisite).where(criteria).limit(pagination.limit).offset(pagination.offset))
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/course_prerequisite/{course_prerequisite_id}", tags=["course_prerequisite"],
            response_model=CoursePrerequisiteOut)
async def get_course_prerequisite(user_auth: CurrentUser, course_prerequisite_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_course_prerequisite = db.scalars(
            select(CoursePrerequisite).where(CoursePrerequisite.id == course_prerequisite_id)).first()
        if db_course_prerequisite:
            return db_course_prerequisite
        raise HTTPException(status_code=404, detail="course prerequisite not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/course_prerequisite/update/{course_prerequisite_id}", tags=["course_prerequisite"],
            response_model=CoursePrerequisiteOut)
async def update_course_prerequisite(
        user_auth: CurrentUser,
        course_prerequisite: CoursePrerequisiteUpdate,
        course_prerequisite_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_course_prerequisite = db.scalars(
                select(CoursePrerequisite).where(CoursePrerequisite.id == course_prerequisite_id)).first()
            if db_course_prerequisite is None:
                raise HTTPException(status_code=404, detail="course prerequisite not found!")
            course_prerequisite_dict = course_prerequisite.model_dump(exclude_unset=True)
            course_prerequisite_dict["record_date"] = datetime.now()
            course_prerequisite_dict["recorder_id"] = user_auth.id
            for key, value in course_prerequisite_dict.items():
                setattr(db_course_prerequisite, key, value)
            db.commit()
            return db_course_prerequisite
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating course prerequisite {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating course prerequisite {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/course_prerequisite/delete/{course_prerequisite_id}", tags=["course_prerequisite"])
async def delete_course_prerequisite(
        user_auth: CurrentUser, course_prerequisite_id: int, db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_course_prerequisite = db.scalars(
            select(CoursePrerequisite).where(CoursePrerequisite.id == course_prerequisite_id)).first()
        if db_course_prerequisite:
            db.delete(db_course_prerequisite)
            db.commit()
            return {"massage": f"course prerequisite with id: {course_prerequisite_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="course prerequisite not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
