from pydantic import BaseModel

from datetime import datetime
from datetime import date

"""
define pydantic models for data validation. to validate 'Request' and 'Response' body. 
all fields in 'Update' models are optional.
'Foreign Keys' are nullable.
"""


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


# permission_group_defines
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
    permission_group_id: int | None = None
    is_enabled: bool | None = True
    recorder_id: int | None = None


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
    recorder_id: int | None = None


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
    permission_group_id: int
    is_enabled: bool
    recorder_id: int | None
    record_date: datetime


# lesson_groups
class LessonGroupIn(BaseModel):
    name: str
    is_enabled: bool | None = True


class LessonGroupUpdate(BaseModel):
    name: str | None = None
    is_enabled: bool | None = None


class LessonGroupOut(BaseModel):
    id: int
    name: str
    is_enabled: bool
    record_date: datetime
