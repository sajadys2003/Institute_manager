from inspect import currentframe
from fastapi import Depends, HTTPException, APIRouter, status
from app.models import LessonGroup
from app.schemas import LessonGroupIn, LessonGroupResponse, LessonGroupUpdate
from app.dependencies import get_session, PageDep
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select
from app.routers.security import get_current_user, authorized
from sqlalchemy.exc import IntegrityError

router = APIRouter()


# Endpoints of lesson group
# add all Endpoints for lesson group
# -------------------------------------------------------------------------------------------------------


@router.post("/", tags=["lessons_group"], response_model=LessonGroupResponse)
async def create_lessons_group(
        user_auth: get_current_user, lesson_group: LessonGroupIn, db: Session = Depends(get_session)
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


@router.get("/", tags=["lessons_group"], response_model=list[LessonGroupResponse])
async def get_lessons_groups(
        user_auth: get_current_user, pagination: PageDep, db: Session = Depends(get_session), search: str | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        criteria = (LessonGroup.name.contains(search) if search else True)
        return db.scalars(select(LessonGroup).where(criteria).limit(pagination.limit).offset(pagination.offset))


@router.get("/{lessons_group_id}", tags=["lessons_group"], response_model=LessonGroupResponse)
async def get_lessons_group_by_id(
        user_auth: get_current_user,
        lessons_group_id: int,
        db: Session = Depends(get_session)
):
    operation = currentframe().f_code.co_name
    if authorized(user_auth, operation):
        db_lessons_group = db.scalars(
            select(LessonGroup).where(LessonGroup.id == lessons_group_id)).first()
        if db_lessons_group:
            return db_lessons_group
        raise HTTPException(status_code=404, detail="lesson group not found!")


@router.put("/{lessons_group_id}", tags=["lessons_group"], response_model=LessonGroupResponse)
async def update_lessons_group(
        user_auth: get_current_user,
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
                raise HTTPException(status_code=404, detail="lessons group not found!")
            lessons_group_dict = lessons_group.model_dump(exclude_unset=True)
            lessons_group_dict["record_date"] = datetime.now()
            lessons_group_dict["recorder_id"] = user_auth.id
            for key, value in lessons_group_dict.items():
                setattr(db_lessons_group, key, value)
            db.commit()
            return db_lessons_group
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"{e.args}")


@router.delete("/{lessons_group_id}", tags=["lessons_group"])
async def delete_lessons_group(user_auth: get_current_user, lessons_group_id: int, db: Session = Depends(get_session)):
    if user_auth.is_super_admin or currentframe().f_code.co_name in user_auth.permissions_list:
        try:
            db_lessons_group = db.scalars(
                select(LessonGroup).where(LessonGroup.id == lessons_group_id)).first()
            if db_lessons_group:
                db.delete(db_lessons_group)
                db.commit()
                return {"massage": f"lessons group with id: {lessons_group_id} successfully deleted"}
            else:
                raise HTTPException(status_code=404, detail="lessons group not found!")
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"integrity error deleting lesson group {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=f"error deleting lesson group {e}")
    raise HTTPException(status_code=401, detail="Not enough permissions")
