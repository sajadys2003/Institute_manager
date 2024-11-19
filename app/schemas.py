from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

# define pydantic models to validate 'Request' and 'Response' body.


# roles
class RoleIn(BaseModel):
    name: str
    is_enabled: bool | None = True


class RoleUpdate(BaseModel):
    name: str | None = None
    is_enabled: bool | None = None


class RoleOut(BaseModel):
    id: int
    name: str
    is_enabled: bool
    record_date: datetime
    recorder_id: int | None


# permissions
class PermissionIn(BaseModel):
    name: str
    parent_id: int | None = None
    is_enabled: bool | None = True


class PermissionUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None
    is_enabled: bool | None = None


class PermissionOut(BaseModel):
    id: int
    name: str
    parent_id: int | None
    is_enabled: bool
    recorder_id: int | None
    record_date: datetime


# permission_groups
class PermissionGroupIn(BaseModel):
    name: str
    is_enabled: bool | None = True


class PermissionGroupUpdate(BaseModel):
    name: str | None = None
    is_enabled: bool | None = None


class PermissionGroupOut(BaseModel):
    id: int
    name: str
    is_enabled: bool
    record_date: datetime


# permission_group_define
class PermissionGroupDefineIn(BaseModel):
    permission_id: int
    permission_group_id: int


class PermissionGroupDefineUpdate(BaseModel):
    permission_id: int | None = None
    permission_group_id: int | None = None


class PermissionGroupDefineOut(BaseModel):
    id: int
    permission_id: int
    permission_group_id: int


# users
class UserIn(BaseModel):
    first_name: str
    last_name: str
    gender: str
    father_name: str
    date_of_birth: date
    national_code: str
    phone_number: str
    role_id: int | None = None
    recruitment_date: datetime
    is_super_admin: bool = False
    is_panel_user: bool = False
    password: str
    permission_group_id: int | None = None
    is_enabled: bool = True


class UserAuth(UserIn):
    permissions_list: list
    id: int


class UserUpdate(BaseModel):
    gender: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    national_code: str | None = None
    phone_number: str | None = None
    password: str | None = None
    role_id: int | None = None
    recruitment_date: datetime | None = None
    is_super_admin: bool | None = None
    is_panel_user: bool | None = None
    permission_group_id: int | None = None
    is_enabled: bool | None = None


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    gender: str
    father_name: str
    date_of_birth: date
    national_code: str
    phone_number: str
    role_id: int | None
    recruitment_date: datetime
    is_super_admin: bool | None
    is_panel_user: bool
    permission_group_id: int | None
    is_enabled: bool
    recorder_id: int | None


# response models

class RoleResponse(RoleOut):
    recorder: UserOut | None


class PermissionResponse(PermissionOut):
    parent: PermissionOut | None
    recorder: UserOut | None


class PermissionGroupResponse(PermissionOut):
    recorder: UserOut | None


class PermissionGroupDefineResponse(PermissionGroupDefineOut):
    permission: PermissionOut
    permission_group: PermissionGroupOut
    recorder: UserOut | None


class UserResponse(UserOut):
    role: RoleOut | None
    permission_group: PermissionGroupOut | None
    recorder: UserOut | None


class LessonsGroupIn(BaseModel):
    name: str


class LessonsGroupUpdate(BaseModel):
    name: str | None


class LessonsGroupOut(BaseModel):
    id: int
    name: str
    record_date: datetime
    recorder: UserOut


class LessonIn(BaseModel):
    name: str
    lesson_group_id: int


class LessonUpdate(BaseModel):
    name: str | None
    lesson_group_id: int | None


class LessonOut(BaseModel):
    id: int
    name: str
    lesson_group: LessonsGroupIn
    record_date: datetime
    recorder: UserOut


class CourseIn(BaseModel):
    name: str
    lesson_id: int


class CourseUpdate(BaseModel):
    name: str | None
    lesson_id: int | None


class CourseOut(BaseModel):
    id: int
    name: str
    lesson: LessonIn
    record_date: datetime
    recorder: UserOut


class CoursePriceIn(BaseModel):
    course_id: int
    public_price: float
    private_price: float
    date: datetime
    duration: float


class CoursePriceUpdate(BaseModel):
    course_id: int | None
    public_price: float | None
    private_price: float | None
    duration: float | None


class CoursePriceOut(BaseModel):
    id: int
    course: CourseIn
    public_price: float
    private_price: float
    date: datetime
    duration: float
    record_date: datetime
    recorder: UserOut


class CoursePrerequisiteIn(BaseModel):
    main_course_id: int
    prerequisite_id: int


class CoursePrerequisiteUpdate(BaseModel):
    main_course_id: int | None
    prerequisite_id: int | None


class CoursePrerequisiteOut(BaseModel):
    id: int
    main_course: CourseIn
    prerequisite: CourseIn
    record_date: datetime
    recorder: UserOut


class PresentationIn(BaseModel):
    course_id: int
    teacher_id: int
    is_private: bool | None = False
    session_count: int
    start_date: date
    end_date: date


class PresentationUpdate(BaseModel):
    course_id: int | None = None
    teacher_id: int | None = None
    is_private: bool | None = None
    session_count: int | None = None
    start_date: date | None = None
    is_enabled: bool | None = None


class PresentationOut(BaseModel):
    course_id: int
    teacher_id: int
    is_private: bool
    session_count: int
    start_date: date
    end_date: date
    recorder_id: int
    record_date: datetime


class SelectedPresentationIn(BaseModel):
    presentation_id: int
    student_id: int | None = None
    grade: float | None = None


class SelectedPresentationUpdate(BaseModel):
    presentation_id: int | None = None
    student_id: int | None = None
    grade: float | None = None


class SelectedPresentationOut(BaseModel):
    id: int
    presentation_id: int
    student_id: int
    grade: float | None
    recorder_id: int
    record_date: datetime


class PresentationSessionIn(BaseModel):
    presentation_id: int
    classroom_id: int
    start_time: datetime
    end_time: datetime
    is_canceled: bool | None = False
    is_extra: bool | None = False


class PresentationSessionUpdate(BaseModel):
    presentation_id: int | None = None
    classroom_id: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    is_canceled: bool | None = None
    is_extra: bool | None = None


class PresentationSessionOut(BaseModel):
    presentation_id: int
    classroom_id: int
    start_time: datetime
    end_time: datetime
    is_canceled: bool
    is_extra: bool
    recorder_id: int | None
    record_date: datetime


class RollCallIn(BaseModel):
    presentation_session_id: int
    student_id: int
    is_present: bool
    delay: int
    comment: str


class RollCallUpdate(BaseModel):
    presentation_session_id: int | None
    student_id: int | None
    is_present: bool | None
    delay: int | None
    comment: str | None


class RollCallOut(BaseModel):
    id: int
    presentation_session: PresentationSessionOut
    student: UserOut
    is_present: bool
    delay: int
    comment: str
    record_date: datetime
    recorder: UserOut


class SurveyCategoryIn(BaseModel):
    name: str


class SurveyCategoryUpdate(BaseModel):
    name: str | None = None


class SurveyCategoryOut(BaseModel):
    id: int
    name: str
    record_date: datetime
    recorder: UserOut


class PresentationSurveyIn(BaseModel):
    student_id: int
    presentation_id: int
    survey_category_id: int
    score: int


class PresentationSurveyUpdate(BaseModel):
    student_id: int | None = None
    presentation_id: int | None = None
    survey_category_id: int | None = None
    score: int | None = None


class PresentationSurveyOut(BaseModel):
    id: int
    student: UserOut
    presentation: PresentationOut
    survey_category: SurveyCategoryIn
    score: int
    recorder: UserOut
    record_date: datetime


class SelectedExamIn(BaseModel):
    student_id: int
    exam_schedule_id: int
    is_participated: bool | None = True
    grade: float | None = None


class SelectedExamUpdate(BaseModel):
    student_id: int | None
    exam_schedule_id: int | None
    is_participated: bool | None = None
    grade: float | None = None


class SelectedExamOut(BaseModel):
    id: int
    student_id: int
    exam_schedule_id: int
    is_participated: bool
    grade: float | None
    recorder_id: int
    record_date: datetime


class FinancialCategoryIn(BaseModel):
    name: str


class FinancialCategoryUpdate(BaseModel):
    name: str | None = None


class FinancialCategoryOut(BaseModel):
    id: int
    name: str
    recorder: UserOut
    record_date: datetime


class PayCategoryIn(BaseModel):
    name: str


class PayCategoryUpdate(BaseModel):
    name: str | None = None


class PayCategoryOut(BaseModel):
    id: int
    name: str
    recorder: UserOut
    record_date: datetime


class FinancialTransactionIn(BaseModel):
    user_id: int
    financial_category_id: int
    amount: Decimal
    presentation_id: int | None = None
    selected_presentation_id: int | None = None
    selected_exam_id: int | None = None
    transaction_date: datetime
    pay_reference: str
    pay_category_id: int


class FinancialTransactionOut(BaseModel):
    id: int
    user: UserOut
    financial_category: FinancialCategoryIn | None = None
    amount: Decimal
    presentation: PresentationOut | None = None
    selected_presentation: SelectedPresentationOut | None = None
    selected_exam: SelectedExamOut | None = None
    transaction_date: datetime
    pay_reference: str
    pay_category: PayCategoryIn | None = None
    recorder: UserOut
    record_date: datetime


class FinancialTransactionUpdate(BaseModel):
    user_id: int | None = None
    financial_category_id: int | None = None
    amount: Decimal | None = None
    presentation_id: int | None = None
    selected_presentation_id: int | None = None
    selected_exam_id: int | None = None
    transaction_date: datetime | None = None
    pay_reference: str | None = None
    pay_category_id: int | None = None


class LoginOut(BaseModel):
    user: UserOut
    login_date: datetime
