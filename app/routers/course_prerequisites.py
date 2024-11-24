from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import CoursePrerequisite
from app.schemas import CoursePrerequisiteIn, CoursePrerequisiteResponse, CoursePrerequisiteUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import authorized, CurrentUser
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/course_prerequisites")


# Endpoints of course price
# add all Endpoints for course price
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["course_prerequisites"], response_model=CoursePrerequisiteResponse)
async def create_course_prerequisite(
        user_auth: CurrentUser, course_prerequisite: CoursePrerequisiteIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["course_prerequisites"], response_model=list[CoursePrerequisiteResponse])
async def get_course_prerequisites(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session),
        main_course_id: int | None = None, prerequisite_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            CoursePrerequisite.main_course_id == main_course_id
            if (main_course_id or main_course_id == 0) else True,
            CoursePrerequisite.prerequisite_id == prerequisite_id
            if (prerequisite_id or prerequisite_id == 0) else True
        )
        return db.scalars(select(CoursePrerequisite).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.put("/", tags=["course_prerequisites"], response_model=CoursePrerequisiteResponse)
async def update_course_prerequisite(
        user_auth: CurrentUser,
        course_prerequisite: CoursePrerequisiteUpdate,
        main_course_id: int,
        prerequisite_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_course_prerequisite = db.scalars(
                select(CoursePrerequisite).where(and_(CoursePrerequisite.prerequisite_id == prerequisite_id,
                                                      CoursePrerequisite.main_course_id == main_course_id))).first()
            if db_course_prerequisite is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course prerequisite not found!")
            course_prerequisite_dict = course_prerequisite.model_dump(exclude_unset=True)
            course_prerequisite_dict["record_date"] = datetime.now()
            course_prerequisite_dict["recorder_id"] = user_auth.id
            for key, value in course_prerequisite_dict.items():
                setattr(db_course_prerequisite, key, value)
            db.commit()
            return db_course_prerequisite
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/", tags=["course_prerequisites"])
async def delete_course_prerequisite(
        user_auth: CurrentUser, prerequisite_id: int, main_course_id: int, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_course_prerequisite = db.scalars(
            select(CoursePrerequisite).where(and_(CoursePrerequisite.prerequisite_id == prerequisite_id,
                                                  CoursePrerequisite.main_course_id == main_course_id))).first()
        if db_course_prerequisite:
            db.delete(db_course_prerequisite)
            db.commit()
            return {"massage": "course prerequisite successfully deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="course prerequisite not found!")
