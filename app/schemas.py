from pydantic import BaseModel
from datetime import datetime
from datetime import date
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


class LessonsGroupResponse(BaseModel):
    id: int
    name: str
    record_date: datetime
    recorder: UserOut


class LessonsGroupUpdate(BaseModel):
    name: str | None


class LessonIn(BaseModel):
    name: str
    lesson_group_id: int


class LessonResponse(BaseModel):
    id: int
    name: str
    lesson_group: LessonsGroupIn
    record_date: datetime
    recorder: UserOut


class LessonUpdate(BaseModel):
    name: str | None
    lesson_group_id: int | None


class CourseIn(BaseModel):
    name: str
    lesson_id: int


class CourseResponse(BaseModel):
    id: int
    name: str
    lesson: LessonIn
    record_date: datetime
    recorder: UserOut


class CourseUpdate(BaseModel):
    name: str | None
    lesson_id: int | None


class CoursePriceIn(BaseModel):
    course_id: int
    public_price: float
    private_price: float
    date: datetime
    duration: float


class CoursePriceResponse(BaseModel):
    id: int
    course: CourseIn
    public_price: float
    private_price: float
    date: datetime
    duration: float
    record_date: datetime
    recorder: UserOut


class CoursePriceUpdate(BaseModel):
    course_id: int | None
    public_price: float | None
    private_price: float | None
    duration: float | None


class CoursePrerequisiteIn(BaseModel):
    main_course_id: int
    prerequisite_id: int


class CoursePrerequisiteResponse(BaseModel):
    id: int
    main_course: CourseIn
    prerequisite: CourseIn
    record_date: datetime
    recorder: UserOut


class CoursePrerequisiteUpdate(BaseModel):
    main_course_id: int | None
    prerequisite_id: int | None


class RollCallIn(BaseModel):
    presentation_session_id: int
    student_id: int
    is_present: bool
    delay: int
    comment: str


class RollCallResponse(BaseModel):
    id: int
    presentation_session: int
    student: UserOut
    is_present: bool
    delay: int
    comment: str
    record_date: datetime
    recorder: UserOut


class RollCallUpdate(BaseModel):
    presentation_session_id: int | None
    student_id: int | None
    is_present: bool | None
    delay: int | None
    comment: str | None


class SurveyCategoryIn(BaseModel):
    name: str


class SurveyCategoryResponse(BaseModel):
    id: int
    name: str
    record_date: datetime
    recorder: UserOut


class SurveyCategoryUpdate(BaseModel):
    name: str | None = None


class PresentationSurveyIn(BaseModel):
    student_id: int
    presentation_id: int
    survey_category_id: int
    score: int


class PresentationSurveyResponse(BaseModel):
    id: int
    student: UserOut
    presentation: int
    survey_category: SurveyCategoryResponse
    score: int
    recorder: int
    record_date: datetime


class PresentationSurveyUpdate(BaseModel):
    student_id: int | None = None
    presentation_id: int | None = None
    survey_category_id: int | None = None
    score: int | None = None


class FinancialCategoryIn(BaseModel):
    name: str


class FinancialCategoryResponse(BaseModel):
    id: int
    name: str
    recorder: UserOut
    record_date: datetime


class FinancialCategoryUpdate(BaseModel):
    name: str | None = None


class PayCategoryIn(BaseModel):
    name: str


class PayCategoryResponse(BaseModel):
    id: int
    name: str
    recorder: UserOut
    record_date: datetime


class PayCategoryUpdate(BaseModel):
    name: str | None = None


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


class FinancialTransactionResponse(BaseModel):
    id: int
    user: UserOut
    financial_category: FinancialCategoryResponse
    amount: Decimal
    presentation: int
    selected_presentation: int
    selected_exam: int
    transaction_date: datetime
    pay_reference: str
    pay_category: PayCategoryResponse
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


class LoginResponse(BaseModel):
    id: int
    user: UserOut
    login_date: datetime
