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
    parent_id: int | None= None
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
    id: int
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


class BuildingIn(BaseModel):
    name: str
    location: str
    is_enabled: bool | None = True


class BuildingUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    is_enabled: bool | None = None


class BuildingOut(BaseModel):
    id: int
    name: str
    location: str
    is_enabled: bool
    recorder_id: int | None
    record_date: datetime


class ClassroomIn(BaseModel):
    name: str
    building_id: int
    floor: str
    capacity: int | None = None
    lesson_group_id: int | None = None
    is_enabled: bool | None = True


class ClassroomUpdate(BaseModel):
    name: str | None = None
    building_id: int | None = None
    floor: str | None = None
    capacity: int | None = None
    lesson_group_id: int | None = None
    is_enabled: bool | None = None


class ClassroomOut(BaseModel):
    id: int
    name: str
    building_id: int
    floor: str
    capacity: int
    lesson_group_id: int
    is_enabled: bool
    recorder_id: int
    record_date: datetime


class PresentationIn(BaseModel):
    course_id: int
    teacher_id: int
    is_private: bool
    session_count: int
    start_date: date
    end_date: date
    is_enabled: bool | None = True


class PresentationUpdate(BaseModel):
    course_id: int | None = None
    teacher_id: int | None = None
    is_private: bool | None = None
    session_count: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_enabled: bool | None = None


class PresentationOut(BaseModel):
    id: int
    course_id: int
    teacher_id: int
    is_private: bool
    session_count: int
    start_date: date
    end_date: date
    is_enabled: bool
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


class BuildingResponse(BuildingOut):
    recorder: UserOut | None


class ClassroomResponse(ClassroomOut):
    building: BuildingOut
    # lesson_group:        ...
    recorder: UserOut


class PresentationResponse(PresentationOut):
    # course:             ...
    teacher: UserOut
    recorder: UserOut
