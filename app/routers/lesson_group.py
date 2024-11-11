from fastapi import Depends, HTTPException
from app.models import LessonGroup
from app.schemas import LessonsGroupIn, LessonsGroupResponse, LessonsGroupUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import select, and_
from app.routers.security import CurrentUser

router = APIRouter()


# Endpoints of lesson group
# add all Endpoints for lesson group
# -------------------------------------------------------------------------------------------------------


@router.post("/lessons_group/create", tags=["lessons_group"], response_model=LessonsGroupResponse)
async def create_lessons_group(
        user_auth: CurrentUser, lesson_group: LessonsGroupIn, db: Session = Depends(get_session)
):
    if user_auth:
        lessons_group_dict = lesson_group.dict()
        lessons_group_dict["record_date"] = datetime.now()
        lessons_group_dict["recorder_id"] = user_auth.id
        db_lessons_group = LessonGroup(**lessons_group_dict)
        db.add(db_lessons_group)
        db.commit()
        db.refresh(db_lessons_group)
        return db_lessons_group
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/lessons_group", tags=["lessons_group"], response_model=list[LessonsGroupResponse])
async def get_lessons_groups(
        user_auth: CurrentUser, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    if user_auth:
        if search:
            criteria = and_(LessonGroup.is_enabled, LessonGroup.name.contains(search))
            lessons_groups = db.scalars(
                select(LessonGroup).where(criteria).limit(pagination.limit).offset(pagination.offset))
            if lessons_groups:
                return lessons_groups
            raise HTTPException(status_code=404, detail="lesson groups not found!")
        lessons_groups = db.scalars(select(LessonGroup).limit(pagination.limit).offset(pagination.offset))
        if lessons_groups:
            return lessons_groups
        raise HTTPException(status_code=404, detail="lesson groups not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.get("/lessons_group/{lessons_group_id}", tags=["lessons_group"], response_model=LessonsGroupResponse)
async def get_lessons_group(user_auth: CurrentUser, lessons_group_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lessons_group = db.scalars(
            select(LessonGroup).where(LessonGroup.id == lessons_group_id).where(LessonGroup.is_enabled)).first()
        if db_lessons_group:
            return db_lessons_group
        raise HTTPException(status_code=404, detail="lesson group not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.put("/lessons_group/update/{lessons_group_id}", tags=["lessons_group"], response_model=LessonsGroupResponse)
async def update_lessons_group(
        user_auth: CurrentUser,
        lessons_group: LessonsGroupUpdate,
        lessons_group_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:
        db_lessons_group = db.scalars(
            select(lessons_group).where(LessonGroup.id == lessons_group_id).where(LessonGroup.is_enabled)).first()
        if db_lessons_group is None:
            raise HTTPException(status_code=404, detail="lessons group not found!")
        lessons_group_dict = lessons_group.model_dump(exclude_unset=True)
        lessons_group_dict["record_date"] = datetime.now()
        lessons_group_dict["recorder_id"] = user_auth.id
        for key, value in lessons_group_dict.items():
            setattr(db_lessons_group, key, value)
        db.commit()
        return db_lessons_group
    raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/lessons_group/delete/{lessons_group_id}", tags=["lessons_group"])
async def delete_lessons_group(user_auth: CurrentUser, lessons_group_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lessons_group = db.scalars(
            select(LessonGroup).where(LessonGroup.id == lessons_group_id).where(LessonGroup.is_enabled)).first()
        if db_lessons_group:
            db_lessons_group.is_enabled = False
            db.commit()
            return {"massage": f"lessons group with id: {lessons_group_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="lessons group not found!")
    raise HTTPException(status_code=401, detail="Not enough permissions")
