from fastapi import FastAPI
from fastapi import APIRouter

# APIRouter, used to group path operations and structure our app in multiple files.
from app.routers import (
    security,
    users,
    roles,
    permissions,
    permission_groups,
    permission_group_defines,
    lesson_groups,
    lessons,
    courses,
    course_prices,
    course_prerequisites,
    buildings,
    classrooms,
    presentations,
    selected_presentations,
    presentation_sessions,
    roll_calls,
    survey_categories,
    presentation_surveys,
    exams,
    exam_schedules,
    selected_exams,
    financial_categories,
    pay_categories,
    financial_transactions,
    holidays
)

app = FastAPI()


def include_routers(routers: list[APIRouter]):
    for router in routers:
        app.include_router(router)


include_routers(
    routers=[
        security.router,
        users.router,
        roles.router,
        permissions.router,
        permission_groups.router,
        permission_group_defines.router,
        lesson_groups.router,
        lessons.router,
        courses.router,
        course_prices.router,
        course_prerequisites.router,
        buildings.router,
        classrooms.router,
        presentations.router,
        selected_presentations.router,
        presentation_sessions.router,
        roll_calls.router,
        survey_categories.router,
        presentation_surveys.router,
        exams.router,
        exam_schedules.router,
        selected_exams.router,
        financial_categories.router,
        pay_categories.router,
        financial_transactions.router,
        holidays.router
    ]
)
