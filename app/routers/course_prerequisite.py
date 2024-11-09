from fastapi import Depends, HTTPException
from app.models import CoursePrerequisite
from app.schemas import CoursePrerequisite, CoursePrerequisiteResponse, CoursePrerequisiteUpdate
from app.dependencies import get_session, CommonsDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_
from app.routers.authentication import AuthorizedUser

router = APIRouter()


# Endpoints of course price
# add all Endpoints for course price
# -------------------------------------------------------------------------------------------------------


@router.post("/course_prerequisite/create", tags=["course_prerequisite"], response_model=CoursePrerequisiteResponse)
async def create_course_prerequisite(
        user_auth: AuthorizedUser, course_prerequisite: CoursePrerequisite, db: Session = Depends(get_session)
):

    if user_auth:
        course_prerequisite_dict = course_prerequisite.dict()
        course_prerequisite_dict["record_date"] = datetime.now()
        course_prerequisite_dict["recorder_id"] = user_auth.id
        db_course_prerequisite = CoursePrerequisite(**course_prerequisite_dict)
        db.add(db_course_prerequisite)
        db.commit()
        db.refresh(db_course_prerequisite)

        return db_course_prerequisite


@router.get("/course_prerequisite", tags=["course_prerequisite"], response_model=list[CoursePrerequisiteResponse])
async def get_course_prerequisites(user_auth: AuthorizedUser, db: Session = Depends(get_session), params=CommonsDep):
    if user_auth:

        if params.q:
            criteria = and_(CoursePrerequisite.is_enabled, CoursePrerequisite.name.contains(params.q))

            return db.scalars(select(CoursePrerequisite).where(criteria).limit(params.size).offset(params.page))

        return db.scalars(select(CoursePrerequisite).limit(params.size).offset(params.page))


@router.get("/course_prerequisite/{course_prerequisite_id}", tags=["course_prerequisite"],
            response_model=CoursePrerequisiteResponse)
async def get_course_price(user_auth: AuthorizedUser, course_prerequisite_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_course_prerequisite = db.scalars(
            select(CoursePrerequisite).where(CoursePrerequisite.id == course_prerequisite_id)).first()
        if db_course_prerequisite:
            return db_course_prerequisite
        raise HTTPException(status_code=404, detail="course prerequisite not found!")


@router.put("/course_prerequisite/update/{course_prerequisite_id}", tags=["course_prerequisite"],
            response_model=CoursePrerequisiteResponse)
async def update_course_price(
        user_auth: AuthorizedUser,
        course_prerequisite: CoursePrerequisiteUpdate,
        course_prerequisite_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:

        db_course_prerequisite = db.scalars(
            select(CoursePrerequisite).where(CoursePrerequisiteUpdate.id == course_prerequisite_id)).first()

        if db_course_prerequisite is None:
            raise HTTPException(status_code=404, detail="course prerequisite not found!")

        course_prerequisite_dict = course_prerequisite.model_dump(exclude_unset=True)
        course_prerequisite_dict["record_date"] = datetime.now()
        course_prerequisite_dict["recorder_id"] = user_auth.id

        for key, value in course_prerequisite:
            setattr(db_course_prerequisite, key, value)

        db.commit()

        return db_course_prerequisite


@router.delete("/course_prerequisite/delete/{course_prerequisite_id}", tags=["course_prerequisite"])
async def delete_course_prerequisite(
        user_auth: AuthorizedUser, course_prerequisite_id: int, db: Session = Depends(get_session)
):
    if user_auth:
        db_course_prerequisite = db.scalars(
            select(CoursePrerequisite).where(CoursePrerequisite.id == course_prerequisite_id)).first()
        if db_course_prerequisite:
            db_course_prerequisite.is_enabled = False
            db.commit()
            return {"massage": f"course prerequisite with id: {course_prerequisite_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="course prerequisite not found!")
