from fastapi import Depends, HTTPException
from app.models import LessonGroup
from app.schemas import LessonsGroup, LessonsGroupResponse
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


@router.post("/lessons_group/create", tags=["lessons_group"], response_model=LessonsGroupResponse)
async def create_lessons_group(lesson_group: LessonsGroup, db: Session = Depends(get_session)):
    lessons_group_dict = lesson_group.dict()
    lessons_group_dict["record_date"] = datetime.now()
    db_lessons_group = LessonGroup(**lessons_group_dict)
    db.add(db_lessons_group)
    db.commit()
    db.refresh(db_lessons_group)

    return db_lessons_group


@router.get("/lessons_group", tags=["lessons_group"], response_model=list[LessonsGroupResponse])
async def get_lessons_groups(user_auth: AuthorizedUser, db: Session = Depends(get_session), params=CommonsDep):
    if user_auth:

        if params.q:
            criteria = and_(LessonGroup.is_enabled, LessonGroup.name.contains(params.q))

            return db.scalars(select(LessonGroup).where(criteria).limit(params.size).offset(params.page))

        return db.scalars(select(LessonGroup).limit(params.size).offset(params.page))


@router.get("/lessons_group/{lessons_group_id}", tags=["lessons_group"], response_model=LessonsGroupResponse)
async def get_lessons_group(user_auth: AuthorizedUser, lessons_group_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lessons_group = db.scalars(select(LessonGroup).where(LessonGroup.id == lessons_group_id)).first()
        if db_lessons_group:
            return db_lessons_group
        raise HTTPException(status_code=404, detail="lessons group not found!")


@router.put("/lessons_group/update/{lessons_group_id}", tags=["lessons_group"], response_model=LessonsGroupResponse)
async def update_lessons_group(
        user_auth: AuthorizedUser,
        lessons_group: LessonsGroup,
        lessons_group_id: int,
        db: Session = Depends(get_session)
):
    if user_auth:

        db_lessons_group = db.scalars(select(lessons_group).where(LessonGroup.id == lessons_group_id)).first()

        if db_lessons_group is None:
            raise HTTPException(status_code=404, detail="lessons group not found!")

        lessons_group_dict = lessons_group.model_dump(exclude_unset=True)
        lessons_group_dict["record_date"] = datetime.now()
        lessons_group_dict["recorder_id"] = user_auth.id

        for key, value in lessons_group:
            setattr(db_lessons_group, key, value)

        db.commit()

        return db_lessons_group


@router.delete("/lessons_group/delete/{lessons_group_id}", tags=["lessons_group"])
async def delete_lessons_group(user_auth: AuthorizedUser, lessons_group_id: int, db: Session = Depends(get_session)):
    if user_auth:
        db_lessons_group = db.scalars(select(LessonGroup).where(LessonGroup.id == lessons_group_id)).first()
        if db_lessons_group:
            db_lessons_group.is_enabled = False
            db.commit()
            return {"massage": f"lessons group with id: {lessons_group_id} successfully deleted"}
        else:
            raise HTTPException(status_code=404, detail="lessons group not found!")
