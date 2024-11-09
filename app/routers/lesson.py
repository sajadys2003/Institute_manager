from fastapi import Depends, HTTPException
from app.models import Lesson
from app.schemas import Lesson, LessonResponse
from app.dependencies import get_session, CommonsDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_
from app.routers.authentication import AuthorizedUser

router = APIRouter()


# Endpoints of users
# add all Endpoints for user
# -------------------------------------------------------------------------------------------------------


@router.post("/lesson/create", tags=["lesson"], response_model=LessonResponse)
async def create_lesson(lesson: Lesson, db: Session = Depends(get_session)):
    lesson_dict = lesson.dict()
    lesson_dict["record_date"] = datetime.now()
    db_lesson = Lesson(**lesson_dict)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)

    return db_lesson


@router.get("/lesson", tags=["lesson"], response_model=list[LessonResponse])
async def get_lessons(user_auth: AuthorizedUser, db: Session = Depends(get_session), params=CommonsDep):
    if user_auth:

        if params.q:
            criteria = and_(Lesson.is_enabled, Lesson.name.contains(params.q))

            return db.scalars(select(Lesson).where(criteria).limit(params.size).offset(params.page))

        return db.scalars(select(Lesson).limit(params.size).offset(params.page))


@router.get("/lesson/{lesson_id}", tags=["lesson"], response_model=LessonResponse)
async def get_lesson(user_auth: AuthorizedUser, lesson_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
        if db_lesson:
            return db_lesson
        raise HTTPException(status_code=404, detail="lesson not found!")


@router.put("/lesson/update/{lesson_id}", tags=["lesson"], response_model=LessonResponse)
async def update_lesson(
        user_auth: AuthorizedUser,
        lesson: Lesson,
        lesson_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:

        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()

        if db_lesson is None:
            raise HTTPException(status_code=404, detail="lesson not found!")

        lesson_dict = lesson.model_dump(exclude_unset=True)
        lesson_dict["record_date"] = datetime.now()
        lesson_dict["recorder_id"] = user_auth.id

        for key, value in lesson:
            setattr(db_lesson, key, value)

        db.commit()

        return db_lesson


@router.delete("/lessons/delete/{lesson_id}", tags=["lesson"])
async def delete_lesson(user_auth: AuthorizedUser, lesson_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
        if db_lesson:
            db_lesson.is_enabled = False
            db.commit()
            return {"massage": f"lesson with id: {lesson_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="lesson not found!")
