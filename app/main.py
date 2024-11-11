from fastapi import FastAPI
from fastapi import APIRouter

from app.routers import roles, users, security, lesson_group, lesson, course, course_price

# APIRouter, used to group path operations and structure our app in multiple files.

app = FastAPI()


def include_routers(routers: list[APIRouter]):
    for router in routers:
        app.include_router(router)


include_routers(
    routers=[
        security.router, users.router, roles.router, lesson_group.router, lesson.router, course.router,
        course_price.router
    ]
)
