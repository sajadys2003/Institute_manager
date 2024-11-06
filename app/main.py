from fastapi import FastAPI
from fastapi import APIRouter

from app.routers import roles


# APIRouter, used to group path operations and structure our app in multiple files.

app = FastAPI()

def include_routers(routers: list[APIRouter]):
    for router in routers:
        app.include_router(router)


include_routers(
    routers=[
        roles.router
    ]
)