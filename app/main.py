from fastapi import FastAPI
from fastapi import APIRouter

from app.routers import (users, security, lesson_group, lesson, course, course_price, course_prerequisite, roll_call,
                         survey_category, presentation_survey, financial_category, pay_category, financial_transaction,
                         login_log)

# APIRouter, used to group path operations and structure our app in multiple files.

app = FastAPI()


def include_routers(routers: list[APIRouter]):
    for router in routers:
        app.include_router(router)


include_routers(
    routers=[
        security.router, users.router, lesson_group.router, lesson.router, course.router, course_price.router,
        course_prerequisite.router, roll_call.router, survey_category.router, presentation_survey.router,
        financial_category.router, pay_category.router, financial_transaction.router, login_log.router
    ]
)
