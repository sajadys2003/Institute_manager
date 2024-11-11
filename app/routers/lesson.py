from fastapi import Depends, HTTPException
from app.models import Lesson
from app.schemas import LessonIn, LessonResponse, LessonUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_
from app.routers.security import CurrentUser

router = APIRouter()


# Endpoints of lesson
# add all Endpoints for lesson
# -------------------------------------------------------------------------------------------------------


@router.post("/lesson/create", tags=["lesson"], response_model=LessonResponse)
async def create_lesson(user_auth: CurrentUser, lesson: LessonIn, db: Session = Depends(get_session)):
    if user_auth:
        lesson_dict = lesson.dict()
        lesson_dict["record_date"] = datetime.now()
        lesson_dict["recorder_id"] = user_auth.id
        db_lesson = Lesson(**lesson_dict)
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/lesson", tags=["lesson"], response_model=list[LessonResponse])
async def get_lessons(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth:
        if search:
            criteria = and_(Lesson.is_enabled, Lesson.name.contains(search))
            lessons = db.scalars(select(Lesson).where(criteria).limit(pagination.limit).offset(pagination.offset))
            if lessons:
                return lessons
            raise HTTPException(status_code=404, detail="lesson not found!")
        lessons = db.scalars(select(Lesson).limit(pagination.limit).offset(pagination.offset))
        if lessons:
            return lessons
        raise HTTPException(status_code=404, detail="lesson not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/lesson/{lesson_id}", tags=["lesson"], response_model=LessonResponse)
async def get_lesson(user_auth: CurrentUser, lesson_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id).where(Lesson.is_enabled)).first()
        if db_lesson:
            return db_lesson
        raise HTTPException(status_code=404, detail="lesson not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/lesson/update/{lesson_id}", tags=["lesson"], response_model=LessonResponse)
async def update_lesson(
        user_auth: CurrentUser,
        lesson: LessonUpdate,
        lesson_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:
        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id).where(Lesson.is_enabled)).first()
        if db_lesson is None:
            raise HTTPException(status_code=404, detail="lesson not found!")
        lesson_dict = lesson.model_dump(exclude_unset=True)
        lesson_dict["record_date"] = datetime.now()
        lesson_dict["recorder_id"] = user_auth.id
        for key, value in lesson_dict.items():
            setattr(db_lesson, key, value)
        db.commit()
        return db_lesson
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/lessons/delete/{lesson_id}", tags=["lesson"])
async def delete_lesson(user_auth: CurrentUser, lesson_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id).where(Lesson.is_enabled)).first()
        if db_lesson:
            db_lesson.is_enabled = False
            db.commit()
            return {"massage": f"lesson with id: {lesson_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="lesson not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
