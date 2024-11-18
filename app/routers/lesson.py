from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter
from app.models import Lesson
from app.schemas import LessonIn, LessonOut, LessonUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select, and_
from app.routers.security import CurrentUser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

router = APIRouter()


# Endpoints of lesson
# add all Endpoints for lesson
# -------------------------------------------------------------------------------------------------------


@router.post("/lesson/create", tags=["lesson"], response_model=LessonOut)
async def create_lesson(user_auth: CurrentUser, lesson: LessonIn, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
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
            raise HTTPException(status_code=400, detail=f"integrity error adding lesson {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error adding lesson {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/lesson", tags=["lesson"], response_model=list[LessonOut])
async def get_lessons(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), name: str | None = None,
        lesson_group_id: int | None = None
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        criteria = and_(
            Lesson.name.contains(name)
            if name else True,
            Lesson.lesson_group_id == lesson_group_id
            if (lesson_group_id or lesson_group_id == 0) else True
        )
        return db.scalars(select(Lesson).where(criteria).limit(pagination.limit).offset(pagination.offset))
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/lesson/{lesson_id}", tags=["lesson"], response_model=LessonOut)
async def get_lesson(user_auth: CurrentUser, lesson_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
        if db_lesson:
            return db_lesson
        raise HTTPException(status_code=404, detail="lesson not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/lesson/update/{lesson_id}", tags=["lesson"], response_model=LessonOut)
async def update_lesson(
        user_auth: CurrentUser,
        lesson: LessonUpdate,
        lesson_id: int,
        db: Session = Depends(get_session)
):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
            if db_lesson is None:
                raise HTTPException(status_code=404, detail="lesson not found!")
            lesson_dict = lesson.model_dump(exclude_unset=True)
            lesson_dict["record_date"] = datetime.now()
            lesson_dict["recorder_id"] = user_auth.id
            for key, value in lesson_dict.items():
                setattr(db_lesson, key, value)
            db.commit()
            return db_lesson
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error updating lesson {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error updating lesson {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/lessons/delete/{lesson_id}", tags=["lesson"])
async def delete_lesson(user_auth: CurrentUser, lesson_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_lesson = db.scalars(select(Lesson).where(Lesson.id == lesson_id)).first()
            if db_lesson:
                db.delete(db_lesson)
                db.commit()
                return {"massage": f"lesson with id: {lesson_id} successfully deleted"}
            else:
                raise HTTPException(status_code=404, detail="lesson not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error deleting lesson {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error deleting lesson {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")
