from pydantic import BaseModel
from datetime import datetime
from datetime import date


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
    is_super_admin: bool
    is_panel_user: bool
    password: str
    permission_group_id: int | None = None
    is_enabled: bool | None = True


class UserUpdate(BaseModel):
    gender: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    national_code: str | None = None
    phone_number: str | None = None
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


class LessonsGroup(BaseModel):
    name: str
    is_enabled: bool


class LessonsGroupResponse(BaseModel):
    name: str
    is_enabled: bool
    record_date: datetime
    recorder: UserOut


class LessonsGroupUpdate(BaseModel):
    name: str | None
    is_enabled: bool | None


class Lesson(BaseModel):
    name: str
    lesson_group_id: int
    is_enabled: bool


class LessonResponse(BaseModel):
    name: str
    lesson_group: LessonsGroup
    is_enabled: bool
    record_date: datetime
    recorder: UserOut


class LessonUpdate(BaseModel):
    name: str | None
    lesson_group_id: int | None
    is_enabled: bool | None


class Course(BaseModel):
    name: str
    lesson_id: int
    is_enabled: bool


class CourseResponse(BaseModel):
    name: str
    lesson: Lesson
    is_enabled: bool
    record_date: datetime
    recorder: UserOut


class CourseUpdate(BaseModel):
    name: str | None
    lesson_id: int | None
    is_enabled: bool | None


class CoursePrice(BaseModel):
    course_id: int
    public_price: float
    private_price: float
    duration: float


class CoursePriceResponse(BaseModel):
    course: Course
    public_price: float
    private_price: float
    date: datetime
    duration: float
    recorder: UserOut


class CoursePriceUpdate(BaseModel):
    course_id: int | None
    public_price: float | None
    private_price: float | None
    duration: float | None


class CoursePrerequisite(BaseModel):
    main_course_id: int
    prerequisite_id: int


class CoursePrerequisiteResponse(BaseModel):
    main_course: Course
    prerequisite: Course
    record_date: datetime
    recorder: UserOut


class CoursePrerequisiteUpdate(BaseModel):
    main_course_id: int | None
    prerequisite_id: int | None


class RollCall(BaseModel):
    presentation_session_id: int
    student_id: int
    is_present: bool
    delay: int
    comment: str


class RollCallResponse(BaseModel):
    presentation_session: Presentation
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
