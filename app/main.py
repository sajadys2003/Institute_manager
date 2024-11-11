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
    buildings,
    classrooms,
    presentations
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
        buildings.router,
        classrooms.router,
        presentations.router
    ]
)
