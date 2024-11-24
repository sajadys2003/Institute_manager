from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

# define pydantic models to validate 'Request' and 'Response' body.


# roles
class RoleIn(BaseModel):
    name: str


class RoleUpdate(BaseModel):
    name: str | None = None


class RoleOut(BaseModel):
    id: int
    name: str
    record_date: datetime
    recorder_id: int | None


# permissions
class PermissionOut(BaseModel):
    id: int
    name: str
    parent_id: int | None


# permission_groups
class PermissionGroupIn(BaseModel):
    name: str


class PermissionGroupUpdate(BaseModel):
    name: str | None = None


class PermissionGroupOut(BaseModel):
    id: int
    name: str
    recorder_id: int
    record_date: datetime


# permission_group_define
class PermissionGroupDefineIn(BaseModel):
    permission_group_id: int
    permission_id: int


class PermissionGroupDefineUpdate(BaseModel):
    permission_group_id: int | None = None
    permission_id: int | None = None


class PermissionGroupDefineOut(BaseModel):
    permission_group_id: int
    permission_id: int
    recorder_id: int
    record_date: datetime


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
    role_id: int | None = None
    recruitment_date: datetime
    is_super_admin: bool = False
    is_panel_user: bool = False
    password: str
    permission_group_id: int | None = None
    is_enabled: bool = True
    record_date: datetime
    recorder_id: int | None


# lesson_groups
class LessonGroupIn(BaseModel):
    name: str


class LessonGroupUpdate(BaseModel):
    name: str | None


class LessonGroupOut(BaseModel):
    id: int
    name: str
    record_date: datetime
    recorder_id: int


# lessons
class LessonIn(BaseModel):
    name: str
    lesson_group_id: int


class LessonUpdate(BaseModel):
    name: str | None
    lesson_group_id: int | None


class LessonOut(BaseModel):
    id: int
    name: str
    lesson_group_id: int
    record_date: datetime
    recorder_id: int


# courses
class CourseIn(BaseModel):
    name: str
    lesson_id: int


class CourseUpdate(BaseModel):
    name: str | None
    lesson_id: int | None


class CourseOut(BaseModel):
    id: int
    name: str
    lesson_id: int
    record_date: datetime
    recorder_id: int


# course_prices
class CoursePriceIn(BaseModel):
    course_id: int
    public_price: float
    private_price: float
    date: datetime | None = None
    duration: float | None = None


class CoursePriceUpdate(BaseModel):
    course_id: int | None
    public_price: float | None
    private_price: float | None
    duration: float | None


class CoursePriceOut(BaseModel):
    id: int
    course_id: int
    public_price: float
    private_price: float
    date: datetime | None = None
    duration: float | None = None
    record_date: datetime
    recorder_id: int


# course_prerequisites
class CoursePrerequisiteIn(BaseModel):
    main_course_id: int
    prerequisite_id: int


class CoursePrerequisiteUpdate(BaseModel):
    main_course_id: int | None
    prerequisite_id: int | None


class CoursePrerequisiteOut(BaseModel):
    main_course_id: int
    prerequisite_id: int
    record_date: datetime
    recorder_id: int


# presentations
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
    id: int
    course_id: int
    teacher_id: int
    is_private: bool | None = False
    session_count: int
    start_date: date
    end_date: date
    recorder_id: int
    record_date: datetime


# selected_presentations
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
    student_id: int | None = None
    grade: float | None = None
    recorder_id: int
    record_date: datetime


# presentation_sessions
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
    id: int
    presentation_id: int
    classroom_id: int
    start_time: datetime
    end_time: datetime
    is_canceled: bool | None = False
    is_extra: bool | None = False
    recorder_id: int | None
    record_date: datetime


# roll_calls
class RollCallIn(BaseModel):
    presentation_session_id: int
    student_id: int
    is_present: bool | None = True
    delay: int | None = None
    comment: str | None = None


class RollCallUpdate(BaseModel):
    presentation_session_id: int | None
    student_id: int | None
    is_present: bool | None
    delay: int | None
    comment: str | None


class RollCallOut(BaseModel):
    presentation_session_id: int
    student_id: int
    is_present: bool | None = True
    delay: int | None = None
    comment: str | None = None
    record_date: datetime
    recorder_id: int


# survey_categories
class SurveyCategoryIn(BaseModel):
    name: str


class SurveyCategoryUpdate(BaseModel):
    name: str | None = None


class SurveyCategoryOut(BaseModel):
    id: int
    name: str
    record_date: datetime
    recorder_id: int


# presentations_survey
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
    student_id: int
    presentation_id: int
    survey_category_id: int
    score: int
    recorder_id: int
    record_date: datetime


# selected_exams
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
    is_participated: bool | None = True
    grade: float | None = None
    recorder_id: int
    record_date: datetime


# financial_categories
class FinancialCategoryIn(BaseModel):
    name: str


class FinancialCategoryUpdate(BaseModel):
    name: str | None = None


class FinancialCategoryOut(BaseModel):
    id: int
    name: str
    recorder_id: int
    record_date: datetime


# pay_categories
class PayCategoryIn(BaseModel):
    name: str


class PayCategoryUpdate(BaseModel):
    name: str | None = None


class PayCategoryOut(BaseModel):
    id: int
    name: str
    recorder_id: int
    record_date: datetime


# financial_transactions
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
    is_enabled: bool | None = True


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
    is_enabled: bool | None = None


class FinancialTransactionOut(BaseModel):
    id: int
    user_id: int
    financial_category_id: int
    amount: Decimal
    presentation_id: int | None = None
    selected_presentation_id: int | None = None
    selected_exam_id: int | None = None
    transaction_date: datetime
    pay_reference: str
    pay_category_id: int
    is_enabled: bool
    recorder_id: int
    record_date: datetime


# response models
class RoleResponse(RoleOut):
    recorder: UserOut


class PermissionResponse(PermissionOut):
    parent: PermissionOut


class PermissionGroupResponse(PermissionGroupOut):
    recorder: UserOut


class PermissionGroupDefineResponse(PermissionGroupDefineOut):
    permission_group: PermissionGroupOut
    permission: PermissionOut
    recorder: UserOut


class UserResponse(UserOut):
    role: RoleOut
    permission_group: PermissionGroupOut
    recorder: UserOut


class LessonGroupResponse(LessonOut):
    recorder: UserOut


class LessonResponse(LessonOut):
    lesson_group: LessonGroupOut
    recorder: UserOut


class CourseResponse(CourseOut):
    lesson: LessonOut
    recorder: UserOut


class CoursePriceResponse(CoursePriceOut):
    course: CourseResponse
    recorder: UserOut


class CoursePrerequisiteResponse(CoursePrerequisiteOut):
    main_course: CourseResponse
    prerequisite: CourseResponse
    recorder: UserOut


class RollCallResponse(RollCallOut):
    student: UserOut
    presentation_session: PresentationSessionOut
    recorder: UserOut


class SurveyCategoryResponse(SurveyCategoryOut):
    recorder: UserOut


class PresentationSurveyResponse(PresentationSurveyOut):
    student: UserOut
    presentation: PresentationOut
    survey_category: SurveyCategoryOut
    recorder: UserOut


class FinancialCategoryResponse(FinancialCategoryOut):
    recorder: UserOut


class PayCategoryResponse(PayCategoryOut):
    recorder: UserOut


class FinancialTransactionResponse(FinancialTransactionOut):
    user: UserOut
    financial_category: FinancialCategoryOut
    presentation: PresentationOut
    selected_presentation: SelectedPresentationOut
    selected_exam: SelectedExamOut
    pay_category: PayCategoryOut
    recorder: UserOut


class LoginLogResponse(BaseModel):
    user: UserOut
    login_date: datetime
