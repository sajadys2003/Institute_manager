from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import LessonGroup
from app.schemas import LessonGroupIn, LessonGroupResponse, LessonGroupUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select
from app.routers.security import CurrentUser, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/lesson_groups")


# Endpoints of lesson group
# add all Endpoints for lesson group
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["lesson_groups"], response_model=LessonGroupResponse)
async def create_lesson_group(
        user_auth: CurrentUser, lesson_group: LessonGroupIn, db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            lessons_group_dict = lesson_group.model_dump()
            lessons_group_dict["record_date"] = datetime.now()
            lessons_group_dict["recorder_id"] = user_auth.id
            db_lessons_group = LessonGroup(**lessons_group_dict)
            db.add(db_lessons_group)
            db.commit()
            db.refresh(db_lessons_group)
            return db_lessons_group
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.get("/", tags=["lesson_groups"], response_model=list[LessonGroupResponse])
async def get_lesson_groups(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = (LessonGroup.name.contains(search) if search else True)
        return db.scalars(select(LessonGroup).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{lesson_group_id}", tags=["lesson_groups"], response_model=LessonGroupResponse)
async def get_lesson_group_by_id(
        user_auth: CurrentUser,
        lessons_group_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_lessons_group = db.scalars(
            select(LessonGroup).where(LessonGroup.id == lessons_group_id)).first()
        if db_lessons_group:
            return db_lessons_group
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lesson group not found!")


@router.put("/{lesson_group_id}", tags=["lesson_groups"], response_model=LessonGroupResponse)
async def update_lesson_group(
        user_auth: CurrentUser,
        lessons_group: LessonGroupUpdate,
        lessons_group_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        try:
            db_lessons_group = db.scalars(
                select(LessonGroup).where(LessonGroup.id == lessons_group_id)).first()
            if db_lessons_group is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lessons group not found!")
            lessons_group_dict = lessons_group.model_dump(exclude_unset=True)
            lessons_group_dict["record_date"] = datetime.now()
            lessons_group_dict["recorder_id"] = user_auth.id
            for key, value in lessons_group_dict.items():
                setattr(db_lessons_group, key, value)
            db.commit()
            return db_lessons_group
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")


@router.delete("/{lesson_group_id}", tags=["lesson_groups"])
async def delete_lesson_group(user_auth: CurrentUser, lessons_group_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_lessons_group = db.scalars(
                select(LessonGroup).where(LessonGroup.id == lessons_group_id)).first()
            if db_lessons_group:
                db.delete(db_lessons_group)
                db.commit()
                return {"massage": f"lesson group with id: {lessons_group_id} successfully deleted"}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lesson group not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.args}")
