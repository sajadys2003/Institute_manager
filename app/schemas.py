from pydantic import BaseModel
from datetime import datetime
from datetime import date
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
class PermissionIn(BaseModel):
    name: str
    parent_id: int | None = None


class PermissionUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None


class PermissionOut(BaseModel):
    id: int
    name: str
    parent_id: int | None
    is_enabled: bool
    record_date: datetime


# permission_groups
class PermissionGroupIn(BaseModel):
    name: str


class PermissionGroupUpdate(BaseModel):
    name: str | None = None


class PermissionGroupOut(BaseModel):
    id: int
    name: str
    recorder_id: int | None
    record_date: datetime


# permission_group_define
class PermissionGroupDefineIn(BaseModel):
    permission_group_id: int
    permission_id: int


class PermissionGroupDefineUpdate(BaseModel):
    permission_id: int | None = None
    permission_group_id: int | None = None


class PermissionGroupDefineOut(BaseModel):
    permission_group_id: int
    permission_id: int


# users
class UserIn(BaseModel):
    password: str
    first_name: str
    last_name: str
    gender: str
    father_name: str
    date_of_birth: date | None = None
    national_code: str
    phone_number: str
    role_id: int | None = None
    recruitment_date: datetime | None = None
    is_super_admin: bool | None = False
    is_panel_user: bool | None = True
    permission_group_id: int | None = None
    is_enabled: bool | None = True


class UserUpdate(BaseModel):
    password: str | None = None
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
    record_date: datetime


# lesson_groups
class LessonGroupIn(BaseModel):
    name: str


class LessonGroupUpdate(BaseModel):
    name: str


class LessonGroupOut(BaseModel):
    id: int
    name: str
    recorder_id: int | None
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
    recorder_id: int | None
    record_date: datetime


# course_prices
class CoursePriceIn(BaseModel):
    course_id: int
    public_price: Decimal
    private_price: Decimal
    date: datetime | None = None
    duration: Decimal | None = Decimal("90")


class CoursePriceUpdate(BaseModel):
    course_id: int | None = None
    public_price: Decimal | None = None
    private_price: Decimal | None = None
    date: datetime | None = None
    duration: Decimal | None = None


class CoursePriceOut(BaseModel):
    id: int
    course_id: int
    public_price: Decimal
    private_price: Decimal
    date: datetime
    duration: Decimal
    recorder_id: int | None
    record_date: datetime


# course_prerequisites
class CoursePrerequisiteIn(BaseModel):
    main_course_id: int
    prerequisite_id: int


class CoursePrerequisiteUpdate(BaseModel):
    main_course_id: int | None
    prerequisite_id: int | None


class CoursePrerequisiteOut(BaseModel):
    course_id: int
    prerequisite_id: int
    recorder_id: int | None
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
    recorder_id: int | None
    record_date: datetime


# classrooms
class ClassroomIn(BaseModel):
    name: str
    building_id: int
    floor: str
    capacity: int | None = None
    lesson_group_id: int | None = None


class ClassroomUpdate(BaseModel):
    name: str | None = None
    building_id: int | None = None
    floor: str | None = None
    capacity: int | None = None
    lesson_group_id: int | None = None


class ClassroomOut(BaseModel):
    id: int
    name: str
    building_id: int
    floor: str
    capacity: int
    lesson_group_id: int | None
    recorder_id: int | None
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
    grade: Decimal | None = None


class SelectedPresentationUpdate(BaseModel):
    presentation_id: int | None = None
    student_id: int | None = None
    grade: Decimal | None = None


class SelectedPresentationOut(BaseModel):
    id: int
    presentation_id: int
    student_id: int
    grade: Decimal | None
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
    score: Decimal


class PresentationSurveyUpdate(BaseModel):
    student_id: int | None = None
    presentation_id: int | None = None
    survey_category_id: int | None = None
    score: Decimal | None = None


class PresentationSurveyOut(BaseModel):
    id: int
    student_id: int
    presentation_id: int
    survey_category_id: int
    score: Decimal
    recorder_id: int
    record_date: datetime


# response models
class RoleResponse(RoleOut):
    recorder: UserOut | None


class PermissionResponse(PermissionOut):
    parent: PermissionOut | None
    recorder: UserOut | None


class PermissionGroupResponse(PermissionGroupOut):
    recorder: UserOut | None


class PermissionGroupDefineResponse(PermissionGroupDefineOut):
    permission: PermissionOut
    permission_group: PermissionGroupOut
    recorder: UserOut | None


class UserResponse(UserOut):
    role: RoleOut | None
    permission_group: PermissionGroupOut | None
    recorder: UserOut | None


class LessonGroupResponse(LessonGroupOut):
    recorder: UserOut | None


class LessonResponse(LessonOut):
    lesson_group: LessonGroupOut | None
    recorder: UserOut | None


class CourseResponse(CourseOut):
    lesson: LessonOut | None
    recorder: UserOut | None


class CoursePriceResponse(CoursePriceOut):
    course: CourseOut
    recorder: UserOut | None


class CoursePrerequisiteResponse(CoursePrerequisiteOut):
    main_course: CourseOut
    prerequisite: CourseOut
    recorder: UserOut | None


class BuildingResponse(BuildingOut):
    recorder: UserOut | None


class ClassroomResponse(ClassroomOut):
    building: BuildingOut
    lesson_group: LessonGroupOut | None
    recorder: UserOut | None


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
