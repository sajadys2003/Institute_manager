from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from datetime import date
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_roles",
        foreign_keys=[recorder_id]
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="role",
        foreign_keys="[User.role_id]",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"Role("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    parent_id = mapped_column(ForeignKey("permissions.id"))

    children: Mapped[list["Permission"]] = relationship(
        back_populates="parent",
        passive_deletes="all"
    )
    parent: Mapped["Permission"] = relationship(
        back_populates="children",
        remote_side=[id]
    )
    permission_group_defines: Mapped[list["PermissionGroupDefine"]] = relationship(
        back_populates="permission",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"Permission("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"parent_id={self.parent_id!r})"
        )


class PermissionGroup(Base):
    __tablename__ = "permission_groups"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_permission_groups",
        foreign_keys=[recorder_id]
    )
    permission_group_defines: Mapped[list["PermissionGroupDefine"]] = relationship(
        back_populates="permission_group",
        passive_deletes="all"
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="permission_group",
        foreign_keys="[User.permission_group_id]",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"PermissionGroup("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class PermissionGroupDefine(Base):
    __tablename__ = "permission_group_defines"

    permission_group_id = mapped_column(ForeignKey("permission_groups.id"), primary_key=True, nullable=False)
    permission_id = mapped_column(ForeignKey("permissions.id"), primary_key=True, nullable=False)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    permission_group: Mapped["PermissionGroup"] = relationship(
        back_populates="permission_group_defines"
    )
    permission: Mapped["Permission"] = relationship(
        back_populates="permission_group_defines"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_permission_group_defines"
    )

    def __repr__(self) -> str:
        return (
            f"PermissionGroupDefine("
            f"permission_group_id={self.permission_group_id!r}, "
            f"permission_id={self.permission_id!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    phone_number: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]  # hashed_password
    first_name: Mapped[str]
    last_name: Mapped[str]
    gender: Mapped[str]
    father_name: Mapped[str]
    date_of_birth: Mapped[date] = mapped_column(nullable=True)
    national_code: Mapped[str]
    role_id = mapped_column(ForeignKey("roles.id"))
    recruitment_date: Mapped[datetime] = mapped_column(nullable=True)
    is_super_admin: Mapped[bool] = mapped_column(default=False)
    is_panel_user: Mapped[bool] = mapped_column(default=True)
    permission_group_id = mapped_column(ForeignKey("permission_groups.id"))
    is_enabled: Mapped[bool] = mapped_column(default=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    role: Mapped["Role"] = relationship(
        back_populates="users",
        foreign_keys=[role_id]
    )
    permission_group: Mapped["PermissionGroup"] = relationship(
        back_populates="users",
        foreign_keys=[permission_group_id]
    )
    recorder_of_users: Mapped[list["User"]] = relationship(
        back_populates="recorder"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_users",
        remote_side=[id]
    )
    recorder_of_roles: Mapped[list["Role"]] = relationship(
        back_populates="recorder",
        foreign_keys="[Role.recorder_id]"
    )
    recorder_of_permission_groups: Mapped[list["PermissionGroup"]] = relationship(
        back_populates="recorder",
        foreign_keys="[PermissionGroup.recorder_id]"
    )
    recorder_of_permission_group_defines: Mapped[list["PermissionGroupDefine"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_lesson_groups: Mapped[list["LessonGroup"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_courses: Mapped[list["Course"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_course_prices: Mapped[list["CoursePrice"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_course_prerequisites: Mapped[list["CoursePrerequisite"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_buildings: Mapped[list["Building"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_classrooms: Mapped[list["Classroom"]] = relationship(
        back_populates="recorder"
    )
    teacher_of_presentations: Mapped[list["Presentation"]] = relationship(
        back_populates="teacher",
        foreign_keys="[Presentation.teacher_id]"
    )
    recorder_of_presentations: Mapped[list["Presentation"]] = relationship(
        back_populates="recorder",
        foreign_keys="[Presentation.recorder_id]"
    )
    student_of_selected_presentations: Mapped[list["SelectedPresentation"]] = relationship(
        back_populates="student",
        foreign_keys="[SelectedPresentation.student_id]"
    )
    recorder_of_selected_presentations: Mapped[list["SelectedPresentation"]] = relationship(
        back_populates="recorder",
        foreign_keys="[SelectedPresentation.recorder_id]"
    )
    recorder_of_presentation_sessions: Mapped[list["PresentationSession"]] = relationship(
        back_populates="recorder"
    )
    student_of_roll_calls: Mapped[list["RollCall"]] = relationship(
        back_populates="student",
        foreign_keys="[RollCall.student_id]"
    )
    recorder_of_roll_calls: Mapped[list["RollCall"]] = relationship(
        back_populates="recorder",
        foreign_keys="[RollCall.recorder_id]"
    )
    recorder_of_survey_categories: Mapped[list["SurveyCategory"]] = relationship(
        back_populates="recorder"
    )
    student_of_presentation_surveys: Mapped[list["PresentationSurvey"]] = relationship(
        back_populates="student",
        foreign_keys="[PresentationSurvey.student_id]"
    )
    recorder_of_presentation_surveys: Mapped[list["PresentationSurvey"]] = relationship(
        back_populates="recorder",
        foreign_keys="[PresentationSurvey.recorder_id]"
    )
    recorder_of_exams: Mapped[list["Exam"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_exam_schedules: Mapped[list["ExamSchedule"]] = relationship(
        back_populates="recorder"
    )
    student_of_selected_exams: Mapped[list["SelectedExam"]] = relationship(
        back_populates="student",
        foreign_keys="[SelectedExam.student_id]"
    )
    recorder_of_selected_exams: Mapped[list["SelectedExam"]] = relationship(
        back_populates="recorder",
        foreign_keys="[SelectedExam.recorder_id]"
    )
    recorder_of_financial_categories: Mapped[list["FinancialCategory"]] = relationship(
        back_populates="recorder"
    )
    recorder_of_pay_categories: Mapped[list["PayCategory"]] = relationship(
        back_populates="recorder"
    )
    user_of_financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="user",
        foreign_keys="[FinancialTransaction.user_id]"
    )
    recorder_of_financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="recorder",
        foreign_keys="[FinancialTransaction.recorder_id]"
    )
    recorder_of_holidays: Mapped[list["Holiday"]] = relationship(
        back_populates="recorder"
    )
    user_of_logins: Mapped[list["LoginLog"]] = relationship(
        back_populates="user"
    )

    @property
    def permissions_list(self) -> list[str]:
        if pg := self.permission_group:
            if pgd := pg.permission_group_defines:
                return [p.permission.name for p in pgd]

    def __repr__(self) -> str:
        return (
            f"User("
            f"id={self.id!r}, "
            f"phone_number={self.phone_number!r}, "
            f"password={self.password}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"gender={self.gender!r}, "
            f"father_name={self.father_name!r}, "
            f"date_of_birth={self.date_of_birth!r}, "
            f"national_code={self.national_code!r}, "
            f"phone_number={self.phone_number!r}, "
            f"role_id={self.role_id!r}, "
            f"recruitment_date={self.recruitment_date!r}, "
            f"is_super_admin={self.is_super_admin!r}, "
            f"is_panel_user={self.is_panel_user!r}, "
            f"permission_group_id={self.permission_group_id!r}, "
            f"is_enabled={self.is_enabled!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class LessonGroup(Base):
    __tablename__ = "lesson_groups"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_lesson_groups"
    )

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="lesson_group",
        passive_deletes="all"
    )
    classrooms: Mapped[list["Classroom"]] = relationship(
        back_populates="lesson_group",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"LessonGroup("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    lesson_group_id = mapped_column(ForeignKey("lesson_groups.id"))
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_lessons"
    )

    lesson_group: Mapped["LessonGroup"] = relationship(
        back_populates="lessons"
    )

    courses: Mapped[list["Course"]] = relationship(
        back_populates="lesson",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"Lesson("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"lesson_group_id={self.lesson_group_id!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    lesson_id = mapped_column(ForeignKey("lessons.id"))
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_courses"
    )

    lesson: Mapped["Lesson"] = relationship(
        back_populates="courses"
    )

    course_prices: Mapped[list["CoursePrice"]] = relationship(
        back_populates="course",
        passive_deletes="all"
    )
    as_main_courses: Mapped[list["CoursePrerequisite"]] = relationship(
        back_populates="main_course",
        foreign_keys="[CoursePrerequisite.main_course_id]",
        passive_deletes="all"
    )
    as_prerequisites: Mapped[list["CoursePrerequisite"]] = relationship(
        back_populates="prerequisite",
        foreign_keys="[CoursePrerequisite.prerequisite_id]",
        passive_deletes="all"
    )
    presentations: Mapped[list["Presentation"]] = relationship(
        back_populates="course",
        passive_deletes="all"
    )
    exam: Mapped["Exam"] = relationship(
        back_populates="course"
    )

    def __repr__(self) -> str:
        return (
            f"Course("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"lesson_id={self.lesson_id!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class CoursePrice(Base):
    __tablename__ = "course_prices"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    course_id = mapped_column(ForeignKey("courses.id"), nullable=False)
    public_price: Mapped[Decimal]
    private_price: Mapped[Decimal]
    date: Mapped[datetime]
    duration: Mapped[int]
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    course: Mapped["Course"] = relationship(
        back_populates="course_prices"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_course_prices"
    )

    def __repr__(self) -> str:
        return (
            f"CoursePrice("
            f"id={self.id!r}, "
            f"course_id={self.course_id!r}, "
            f"public_price={self.public_price!r}, "
            f"private_price={self.private_price!r}, "
            f"date={self.date!r}, "
            f"duration={self.duration!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    main_course_id = mapped_column(ForeignKey("courses.id"), primary_key=True, nullable=False)
    prerequisite_id = mapped_column(ForeignKey("courses.id"), primary_key=True, nullable=False)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_course_prerequisites"
    )

    main_course: Mapped["Course"] = relationship(
        back_populates="as_main_courses",
        foreign_keys=[main_course_id]
    )
    prerequisite: Mapped["Course"] = relationship(
        back_populates="as_prerequisites",
        foreign_keys=[prerequisite_id]
    )

    def __repr__(self) -> str:
        return (
            f"CoursePrerequisite("
            f"main_course_id={self.main_course_id!r}, "
            f"prerequisite_id={self.prerequisite_id!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    location: Mapped[str] = mapped_column(nullable=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_buildings"
    )

    classrooms: Mapped[list["Classroom"]] = relationship(
        back_populates="building",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"Building("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"location={self.location!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    building_id = mapped_column(ForeignKey("buildings.id"), nullable=False)
    floor: Mapped[int]
    capacity: Mapped[int]
    lesson_group_id = mapped_column(ForeignKey("lesson_groups.id"))
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_classrooms"
    )

    building: Mapped["Building"] = relationship(
        back_populates="classrooms"
    )
    lesson_group: Mapped["LessonGroup"] = relationship(
        back_populates="classrooms"
    )
    presentation_sessions: Mapped[list["PresentationSession"]] = relationship(
        back_populates="classroom",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"Classroom("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"building_id={self.building_id!r}, "
            f"floor={self.floor!r}, "
            f"capacity={self.capacity!r}, "
            f"lesson_group_id={self.lesson_group_id!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Presentation(Base):
    __tablename__ = "presentations"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    course_id = mapped_column(ForeignKey("courses.id"), nullable=False)
    teacher_id = mapped_column(ForeignKey("users.id"), nullable=False)
    is_private: Mapped[bool]
    session_count: Mapped[int]
    start_date: Mapped[date]
    end_date: Mapped[date]
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    course: Mapped["Course"] = relationship(
        back_populates="presentations"
    )
    teacher: Mapped["User"] = relationship(
        back_populates="teacher_of_presentations",
        foreign_keys=[teacher_id]
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_presentations",
        foreign_keys=[recorder_id]
    )
    selected_presentations: Mapped[list["SelectedPresentation"]] = relationship(
        back_populates="presentation",
        passive_deletes="all"
    )
    presentation_sessions: Mapped[list["PresentationSession"]] = relationship(
        back_populates="presentation",
        passive_deletes="all"
    )
    presentation_surveys: Mapped[list["PresentationSurvey"]] = relationship(
        back_populates="presentation",
        passive_deletes="all"
    )
    financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="presentation",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"Presentation("
            f"id={self.id!r}, "
            f"course_id={self.course_id!r}, "
            f"teacher_id={self.teacher_id!r}, "
            f"is_private={self.is_private!r}, "
            f"session_count={self.session_count!r}, "
            f"start_date={self.start_date!r}, "
            f"end_date={self.end_date!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class SelectedPresentation(Base):
    __tablename__ = "selected_presentations"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    presentation_id = mapped_column(ForeignKey("presentations.id"), nullable=False)
    student_id = mapped_column(ForeignKey("users.id"), nullable=False)
    grade: Mapped[Decimal] = mapped_column(nullable=True)
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    presentation: Mapped["Presentation"] = relationship(
        back_populates="selected_presentations"
    )
    student: Mapped["User"] = relationship(
        back_populates="student_of_selected_presentations",
        foreign_keys=[student_id]
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_selected_presentations",
        foreign_keys=[recorder_id]
    )
    financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="selected_presentation",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"SelectedPresentation("
            f"id={self.id!r}, "
            f"presentation_id={self.presentation_id!r}, "
            f"student_id={self.student_id!r}, "
            f"grade={self.grade!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class PresentationSession(Base):
    __tablename__ = "presentation_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    presentation_id = mapped_column(ForeignKey("presentations.id"), nullable=False)
    classroom_id = mapped_column(ForeignKey("classrooms.id"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    is_canceled: Mapped[bool] = mapped_column(default=False)
    is_extra: Mapped[bool] = mapped_column(default=False)
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    presentation: Mapped["Presentation"] = relationship(
        back_populates="presentation_sessions"
    )
    classroom: Mapped["Classroom"] = relationship(
        back_populates="presentation_sessions"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_presentation_sessions"
    )
    roll_calls: Mapped[list["RollCall"]] = relationship(
        back_populates="presentation_session",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"PresentationSession("
            f"id={self.id!r}, "
            f"presentation_id={self.presentation_id!r}, "
            f"classroom_id={self.classroom_id!r}, "
            f"start_time={self.start_time!r}, "
            f"end_time={self.end_time!r}, "
            f"is_canceled={self.is_canceled!r}, "
            f"is_extra={self.is_extra!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class RollCall(Base):
    __tablename__ = "roll_calls"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    presentation_session_id = mapped_column(ForeignKey("presentation_sessions.id"), nullable=False)
    student_id = mapped_column(ForeignKey("users.id"), nullable=False)
    is_present: Mapped[bool]
    delay: Mapped[int] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    presentation_session: Mapped["PresentationSession"] = relationship(
        back_populates="roll_calls"
    )
    student: Mapped["User"] = relationship(
        back_populates="student_of_roll_calls",
        foreign_keys=[student_id]
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_roll_calls",
        foreign_keys=[recorder_id]
    )

    def __repr__(self) -> str:
        return (
            f"RollCall("
            f"id={self.id!r}, "
            f"presentation_session_id={self.presentation_session_id!r}, "
            f"student_id={self.student_id!r}, "
            f"is_present={self.is_present!r}, "
            f"delay={self.delay!r}, "
            f"comment={self.comment!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class SurveyCategory(Base):
    __tablename__ = "survey_categories"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_survey_categories"
    )

    presentation_surveys: Mapped[list["PresentationSurvey"]] = relationship(
        back_populates="survey_category",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"SurveyCategory("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class PresentationSurvey(Base):
    __tablename__ = "presentation_surveys"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    student_id = mapped_column(ForeignKey("users.id"), nullable=False)
    presentation_id = mapped_column(ForeignKey("presentations.id"), nullable=False)
    survey_category_id = mapped_column(ForeignKey("survey_categories.id"), nullable=False)
    score: Mapped[Decimal]
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    student: Mapped["User"] = relationship(
        back_populates="student_of_presentation_surveys",
        foreign_keys=[student_id]
    )
    presentation: Mapped["Presentation"] = relationship(
        back_populates="presentation_surveys"
    )
    survey_category: Mapped["SurveyCategory"] = relationship(
        back_populates="presentation_surveys"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_presentation_surveys",
        foreign_keys=[recorder_id]
    )

    def __repr__(self) -> str:
        return (
            f"PresentationSurvey("
            f"id={self.id!r}, "
            f"student_id={self.student_id!r}, "
            f"presentation_id={self.presentation_id!r}, "
            f"survey_category_id={self.survey_category_id!r}, "
            f"score={self.score!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    course_id = mapped_column(ForeignKey("courses.id"), nullable=False)
    price: Mapped[Decimal]
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    course: Mapped["Course"] = relationship(
        back_populates="exam"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_exams"
    )
    exam_schedules: Mapped[list["ExamSchedule"]] = relationship(
        back_populates="exam",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"Exam("
            f"id={self.id!r}, "
            f"course_id={self.course_id!r}, "
            f"price={self.price!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    exam_id = mapped_column(ForeignKey("exams.id"), nullable=False)
    start_date: Mapped[datetime]
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    exam: Mapped["Exam"] = relationship(
        back_populates="exam_schedules"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_exam_schedules"
    )
    selected_exams: Mapped[list["SelectedExam"]] = relationship(
        back_populates="exam_schedule",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"ExamSchedule("
            f"id={self.id!r}, "
            f"exam_id={self.exam_id!r}, "
            f"start_date={self.start_date!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class SelectedExam(Base):
    __tablename__ = "selected_exams"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    student_id = mapped_column(ForeignKey("users.id"), nullable=False)
    exam_schedule_id = mapped_column(ForeignKey("exam_schedules.id"), nullable=False)
    is_participated: Mapped[bool] = mapped_column(default=True)
    grade: Mapped[Decimal] = mapped_column(nullable=True)
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    student: Mapped["User"] = relationship(
        back_populates="student_of_selected_exams",
        foreign_keys=[student_id]
    )
    exam_schedule: Mapped["ExamSchedule"] = relationship(
        back_populates="selected_exams"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_selected_exams",
        foreign_keys=[recorder_id]
    )
    financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="selected_exam",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"SelectedExam("
            f"id={self.id!r}, "
            f"student_id={self.student_id!r}, "
            f"exam_schedule_id={self.exam_schedule_id!r}, "
            f"is_participated={self.is_participated!r}, "
            f"grade={self.grade!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class FinancialCategory(Base):
    __tablename__ = "financial_categories"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_financial_categories"
    )

    financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="financial_category",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"FinancialCategory("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class PayCategory(Base):
    __tablename__ = "pay_categories"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_pay_categories"
    )

    financial_transactions: Mapped[list["FinancialTransaction"]] = relationship(
        back_populates="pay_category",
        passive_deletes="all"
    )

    def __repr__(self) -> str:
        return (
            f"PayCategory("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id = mapped_column(ForeignKey("users.id"), nullable=False)
    financial_category_id = mapped_column(ForeignKey("financial_categories.id"), nullable=False)
    amount: Mapped[Decimal]
    presentation_id = mapped_column(ForeignKey("presentations.id"))
    selected_presentation_id = mapped_column(ForeignKey("selected_presentations.id"))
    selected_exam_id = mapped_column(ForeignKey("selected_exams.id"))
    transaction_date: Mapped[datetime] = mapped_column(default=datetime.now())
    pay_reference: Mapped[str] = mapped_column(nullable=True)
    pay_category_id = mapped_column(ForeignKey("pay_categories.id"), nullable=False)
    recorder_id = mapped_column(ForeignKey("users.id"), nullable=False)
    record_date: Mapped[datetime]

    user: Mapped["User"] = relationship(
        back_populates="user_of_financial_transactions",
        foreign_keys=[user_id]
    )
    financial_category: Mapped["FinancialCategory"] = relationship(
        back_populates="financial_transactions"
    )
    presentation: Mapped["Presentation"] = relationship(
        back_populates="financial_transactions"
    )
    selected_presentation: Mapped["SelectedPresentation"] = relationship(
        back_populates="financial_transactions"
    )
    selected_exam: Mapped["SelectedExam"] = relationship(
        back_populates="financial_transactions"
    )
    pay_category: Mapped["PayCategory"] = relationship(
        back_populates="financial_transactions"
    )
    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_financial_transactions",
        foreign_keys=[recorder_id]
    )

    def __repr__(self) -> str:
        return (
            f"FinancialTransaction("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"financial_category_id={self.financial_category_id!r}, "
            f"amount={self.amount!r}, "
            f"presentation_id={self.presentation_id!r}, "
            f"selected_presentation_id={self.selected_presentation_id!r}, "
            f"selected_exam_id={self.selected_exam_id!r}, "
            f"transaction_date={self.transaction_date!r}, "
            f"pay_reference={self.pay_reference!r}, "
            f"pay_category_id={self.pay_category_id!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class Holiday(Base):
    __tablename__ = "holidays"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    holiday_date: Mapped[date]
    recorder_id = mapped_column(ForeignKey("users.id"))
    record_date: Mapped[datetime]

    recorder: Mapped["User"] = relationship(
        back_populates="recorder_of_holidays"
    )

    def __repr__(self) -> str:
        return (
            f"Holiday("
            f"id={self.id!r}, "
            f"holiday_date={self.holiday_date!r}, "
            f"recorder_id={self.recorder_id!r}, "
            f"record_date={self.record_date!r})"
        )


class LoginLog(Base):
    __tablename__ = "login_logs"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id = mapped_column(ForeignKey("users.id"), nullable=False)
    login_date: Mapped[datetime]

    user: Mapped["User"] = relationship(
        back_populates="user_of_logins"
    )

    def __repr__(self) -> str:
        return (
            f"Login("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"login_date={self.login_date!r})"
        )


pg_url = "postgresql+psycopg://postgres:password@localhost:5432/institute"
engine = create_engine(pg_url)

Base.metadata.create_all(bind=engine)  # creates all tables in our database