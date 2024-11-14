from app.models import SelectedExam
from app.schemas import SelectedExamIn, SelectedExamUpdate, SelectedExamResponse


from .security import CurrentUer, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException, status
from app.dependencies import SessionDep, PageDep
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/selected_exams")


async def get_by_id(db: SessionDep, selected_exam_id: int) -> SelectedExam:
    stored_record = db.get(SelectedExam, selected_exam_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[SelectedExamResponse])
async def get_all_selected_exams(
        db: SessionDep,
        page: PageDep,
        current_user: CurrentUer,
        exam_schedule_id: int | None = None
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if exam_schedule_id:
            criteria = SelectedExam.exam_schedule_id == exam_schedule_id
            stored_records = db.query(SelectedExam).where(criteria)

        else:
            stored_records = db.query(SelectedExam)
        return stored_records.offset(page.offset).limit(page.limit).all()


@router.get(path="/{selected_exam_id}", response_model=SelectedExamResponse)
async def get_selected_exam_by_id(
        db: SessionDep,
        selected_exam_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, selected_exam_id)
        return stored_record


@router.post(path="/", response_model=SelectedExamResponse, status_code=status.HTTP_201_CREATED)
async def create_selected_exam(
        db: SessionDep,
        data: SelectedExamIn,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if not data.student_id:
            data.student_id = current_user.id

        data_dict = data.model_dump()
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            new_record = SelectedExam(**data_dict)
            db.add(new_record)
            db.commit()
            return new_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.put(path="/{selected_exam_id}", response_model=SelectedExamResponse)
async def update_selected_exam(
        db: SessionDep,
        selected_presentation_id: int,
        data: SelectedExamUpdate,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        stored_record = await get_by_id(db, selected_presentation_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict.update({"recorder_id": current_user.id, "record_date": datetime.now()})
        try:
            for key, value in data_dict.items():
                setattr(stored_record, key, value)
            db.commit()
            return stored_record
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")


@router.delete(path="/{selected_exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_selected_exam(
        db: SessionDep,
        selected_exam_id: int,
        current_user: CurrentUer
):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, selected_exam_id)
        try:
            db.delete(stored_record)
            db.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{e.args}")
