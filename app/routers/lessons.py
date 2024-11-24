from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import Lesson
from app.schemas import LessonIn, LessonResponse, LessonUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/lessons")


# Endpoints of lesson
# add all Endpoints for lesson
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["lessons"], response_model=LessonResponse)
async def create_lesson(user_auth: CurrentUser, lesson: LessonIn, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            lesson_dict = lesson.model_dump()
            lesson_dict["record_date"] = datetime.now()
            lesson_dict["recorder_id"] = user_auth.id
            db_lesson = Lesson(**lesson_dict)
            db.add(db_lesson)
            db.commit()
            db.refresh(db_lesson)
            return db_lesson
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["lessons"], response_model=list[LessonResponse])
async def get_lessons(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), name: str | None = None,
        lesson_group_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = and_(
            Lesson.name.contains(name)
            if name else True,
            Lesson.lesson_group_id == lesson_group_id
            if (lesson_group_id or lesson_group_id == 0) else True
        )
        return db.scalars(select(Lesson).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{lesson_id}", tags=["lessons"], response_model=LessonResponse)
async def get_lesson_by_id(user_auth: CurrentUser, lesson_id: int, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
        if db_lesson:
            return db_lesson
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lesson not found!")


@router.put("/{lesson_id}", tags=["lessons"], response_model=LessonResponse)
async def update_lesson(
        user_auth: CurrentUser,
        lesson: LessonUpdate,
        lesson_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
            if db_lesson is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lesson not found!")
            lesson_dict = lesson.model_dump(exclude_unset=True)
            lesson_dict["record_date"] = datetime.now()
            lesson_dict["recorder_id"] = user_auth.id
            for key, value in lesson_dict.items():
                setattr(db_lesson, key, value)
            db.commit()
            return db_lesson
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{lesson_id}", tags=["lessons"])
async def delete_lesson(user_auth: CurrentUser, lesson_id: int, db: Session = Depends(get_session)):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
            if db_lesson:
                db.delete(db_lesson)
                db.commit()
                return {"massage": f"lesson with id: {lesson_id} successfully deleted"}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lesson not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")
