from fastapi import FastAPI
from fastapi import APIRouter

from src.routers import roles
from src.routers import permissions
from src.routers import permission_groups
from src.routers import permission_group_defines

"""
APIRouter, used to group path operations, to structure our app in multiple files.
It would then be included in the FastAPI app
"""

app = FastAPI()


def include_routers(routers: list[APIRouter]):
    for router in routers:
        app.include_router(router)


include_routers(
    routers=[
        roles.router,
        permissions.router,
        permission_groups.router,
        permission_group_defines.router
    ]
)
