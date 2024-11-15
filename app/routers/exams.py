from app.models import Exam
from app.schemas import ExamIn, ExamUpdate, ExamResponse

from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/exams")


async def get_by_id(db: SessionDep, exam_id: int) -> Exam:
    stored_record = db.get(Exam, exam_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[ExamResponse])
async def get_all_exams(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        course_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        criteria = Exam.course_id == course_id if (course_id or course_id == 0) else True
        stored_records = db.query(Exam).where(criteria)

        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{exam_id}", response_model=ExamResponse)
async def get_exam_by_id(
        db: SessionDep,
        exam_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, exam_id)
        return stored_record


@router.post(path="/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
        db: SessionDep,
        data: ExamIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = Exam(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{exam_id}", response_model=ExamResponse)
async def update_exam(
        db: SessionDep,
        exam_id: int,
        data: ExamUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, exam_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
        db: SessionDep,
        exam_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, exam_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
