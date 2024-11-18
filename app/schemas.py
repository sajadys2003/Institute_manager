from pydantic import BaseModel
from datetime import datetime, date


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
    recorder_id: int


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
    phone_number: str
    password: str
    first_name: str
    last_name: str
    gender: str
    father_name: str
    date_of_birth: date | None = None
    national_code: str
    role_id: int | None = None
    recruitment_date: datetime | None = None
    is_super_admin: bool | None = False
    is_panel_user: bool | None = True
    permission_group_id: int | None = None
    is_enabled: bool | None = True


class UserUpdate(BaseModel):
    phone_number: str | None = None
    password: str | None = None
    gender: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    national_code: str | None = None
    role_id: int | None = None
    recruitment_date: datetime | None = None
    is_super_admin: bool | None = None
    is_panel_user: bool | None = None
    permission_group_id: int | None = None
    is_enabled: bool | None = None


class UserOut(BaseModel):
    id: int
    phone_number: str
    first_name: str
    last_name: str
    gender: str
    father_name: str
    date_of_birth: date
    national_code: str
    role_id: int | None
    recruitment_date: datetime
    is_super_admin: bool | None
    is_panel_user: bool
    permission_group_id: int | None
    is_enabled: bool
    recorder_id: int | None
    record_date: datetime


# lesson_groups
class LessonGroupIn(BaseModel):
    name: str


class LessonGroupUpdate(BaseModel):
    name: str


class LessonGroupOut(BaseModel):
    id: int
    name: str
    recorder_id: int
    record_date: datetime


# lessons
class LessonIn(BaseModel):
    name: str
    lesson_group_id: int | None = None


class LessonUpdate(BaseModel):
    name: str | None = None
    lesson_group_id: int | None = None


class LessonOut(BaseModel):
    id: int
    name: str
    lesson_group_id: int | None
    record_date: datetime


# courses
class CourseIn(BaseModel):
    name: str
    lesson_id: int | None = None


class CourseUpdate(BaseModel):
    name: str | None = None
    lesson_id: int | None = None


class CourseOut(BaseModel):
    id: int
    name: str
    lesson_id: int | None
    recorder_id: int
    record_date: datetime


# course_prices
class CoursePriceIn(BaseModel):
    course_id: int
    public_price: float
    private_price: float
    date: datetime | None = None
    duration: int | None = 90


class CoursePriceUpdate(BaseModel):
    course_id: int | None = None
    public_price: float | None = None
    private_price: float | None = None
    date: datetime | None = None
    duration: int | None = None


class CoursePriceOut(BaseModel):
    id: int
    course_id: int
    public_price: float
    private_price: float
    date: datetime
    duration: int
    recorder_id: int
    record_date: datetime


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
    recorder_id: int
    record_date: datetime


# buildings
class BuildingIn(BaseModel):
    name: str
    location: str


class BuildingUpdate(BaseModel):
    name: str | None = None
    location: str | None = None


class BuildingOut(BaseModel):
    id: int
    name: str
    location: str
    recorder_id: int
    record_date: datetime


# classrooms
class ClassroomIn(BaseModel):
    name: str
    building_id: int
    floor: int
    capacity: int | None = None
    lesson_group_id: int | None = None


class ClassroomUpdate(BaseModel):
    name: str | None = None
    building_id: int | None = None
    floor: int | None = None
    capacity: int | None = None
    lesson_group_id: int | None = None


class ClassroomOut(BaseModel):
    id: int
    name: str
    building_id: int
    floor: int
    capacity: int
    lesson_group_id: int | None
    recorder_id: int
    record_date: datetime


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
    is_private: bool
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
    student_id: int
    grade: float | None
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
    is_canceled: bool
    is_extra: bool
    recorder_id: int
    record_date: datetime


# roll_calls
class RollCallIn(BaseModel):
    presentation_session_id: int
    student_id: int
    is_present: bool | None = True
    delay: int | None = None
    comment: str | None = None


class RollCallUpdate(BaseModel):
    presentation_session_id: int | None = None
    student_id: int | None = None
    is_present: bool | None = None
    delay: int | None = None
    comment: str | None = None


class RollCallOut(BaseModel):
    id: int
    presentation_session_id: int
    student_id: int
    is_present: bool
    delay: int | None
    comment: str | None
    recorder_id: int
    record_date: datetime


# survey_categories
class SurveyCategoryIn(BaseModel):
    name: str


class SurveyCategoryUpdate(BaseModel):
    name: str | None = None


class SurveyCategoryOut(BaseModel):
    id: int
    name: str
    recorder_id: int
    record_date: datetime


# presentation_surveys
class PresentationSurveyIn(BaseModel):
    student_id: int
    presentation_id: int
    survey_category_id: int
    score: float


class PresentationSurveyUpdate(BaseModel):
    student_id: int | None = None
    presentation_id: int | None = None
    survey_category_id: int | None = None
    score: float | None = None


class PresentationSurveyOut(BaseModel):
    id: int
    student_id: int
    presentation_id: int
    survey_category_id: int
    score: float
    recorder_id: int
    record_date: datetime


# exams
class ExamIn(BaseModel):
    course_id: int
    price: float


class ExamUpdate(BaseModel):
    course_id: int | None = None
    price: float | None = None


class ExamOut(BaseModel):
    id: int
    course_id: int
    price: float
    recorder_id: int
    record_date: datetime


# exam_schedules
class ExamScheduleIn(BaseModel):
    exam_id: int
    start_date: date


class ExamScheduleUpdate(BaseModel):
    exam_id: int | None = None
    start_date: date | None = None


class ExamScheduleOut(BaseModel):
    id: int
    exam_id: int
    start_date: datetime
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
    is_participated: bool
    grade: float | None
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
    amount: float
    presentation_id: int | None = None
    selected_presentation_id: int | None = None
    selected_exam_id: int | None = None
    transaction_date: datetime | None = None
    pay_reference: str | None = None
    pay_category_id: int


class FinancialTransactionUpdate(BaseModel):
    user_id: int | None = None
    financial_category_id: int | None = None
    amount: float | None = None
    presentation_id: int | None = None
    selected_presentation_id: int | None = None
    selected_exam_id: int | None = None
    transaction_date: datetime | None = None
    pay_reference: str | None = None
    pay_category_id: int | None = None


class FinancialTransactionOut(BaseModel):
    id: int
    user_id: int
    financial_category_id: int
    amount: float
    presentation_id: int | None
    selected_presentation_id: int | None
    selected_exam_id: int | None
    transaction_date: datetime | None
    pay_reference: str | None
    pay_category_id: int
    recorder_id: int
    record_date: datetime


# holidays
class HolidayIn(BaseModel):
    holiday_date: date


class HolidayUpdate(BaseModel):
    holiday_date: date | None = None


class HolidayOut(BaseModel):
    id: int
    holiday_date: date
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
    role: RoleOut | None
    permission_group: PermissionGroupOut | None
    recorder: UserOut | None


class LessonGroupResponse(LessonGroupOut):
    recorder: UserOut


class LessonResponse(LessonOut):
    lesson_group: LessonGroupOut | None
    recorder: UserOut


class CourseResponse(CourseOut):
    lesson: LessonOut | None
    recorder: UserOut


class CoursePriceResponse(CoursePriceOut):
    course: CourseOut
    recorder: UserOut


class CoursePrerequisiteResponse(CoursePrerequisiteOut):
    main_course: CourseOut
    prerequisite: CourseOut
    recorder: UserOut


class BuildingResponse(BuildingOut):
    recorder: UserOut


class ClassroomResponse(ClassroomOut):
    building: BuildingOut
    lesson_group: LessonGroupOut | None
    recorder: UserOut


class PresentationResponse(PresentationOut):
    course: CourseOut
    teacher: UserOut
    recorder: UserOut


class SelectedPresentationResponse(SelectedPresentationOut):
    presentation: PresentationOut
    student: UserOut
    recorder: UserOut


class PresentationSessionResponse(PresentationSessionOut):
    presentation: PresentationOut
    classroom: ClassroomOut
    recorder: UserOut


class RollCallResponse(RollCallOut):
    presentation_session: PresentationSessionOut
    student: UserOut
    recorder: UserOut


class SurveyCategoryResponse(SurveyCategoryOut):
    recorder: UserOut


class PresentationSurveyResponse(PresentationSurveyOut):
    student: UserOut
    presentation: PresentationOut
    survey_category: SurveyCategoryOut
    recorder: UserOut


class ExamResponse(ExamOut):
    course: CourseOut
    recorder: UserOut


class ExamScheduleResponse(ExamScheduleOut):
    exam: ExamOut
    recorder: UserOut


class SelectedExamResponse(SelectedExamOut):
    exam_schedule: ExamScheduleOut
    student: UserOut
    recorder: UserOut


class FinancialCategoryResponse(FinancialCategoryOut):
    recorder: UserOut


class PayCategoryResponse(PayCategoryOut):
    recorder: UserOut


class FinancialTransactionResponse(FinancialTransactionOut):
    user: UserOut
    financial_category: FinancialCategoryOut
    presentation: PresentationOut | None
    selected_presentation: SelectedPresentationOut | None
    selected_exam: SelectedExamOut | None
    pay_category: PayCategoryOut
    recorder: UserOut


class HolidayResponse(HolidayOut):
    recorder: UserOut
