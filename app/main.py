from fastapi import FastAPI, APIRouter

from app.routers import (users, security, lesson_groups, lessons, courses, course_prices, course_prerequisites,
                         roll_calls, survey_categories, presentation_surveys, financial_categories, pay_categories,
                         financial_transactions, login_logs)

# APIRouter, used to group path operations and structure our app in multiple files.

app = FastAPI()


def include_routers(routers: list[APIRouter]):
    for router in routers:
        app.include_router(router)


include_routers(
    routers=[
        security.router, users.router, lesson_groups.router, lessons.router, courses.router, course_prices.router,
        course_prerequisites.router, roll_calls.router, survey_categories.router, presentation_surveys.router,
        financial_categories.router, pay_categories.router, financial_transactions.router, login_logs.router
    ]
)
