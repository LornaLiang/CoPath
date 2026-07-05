from fastapi import APIRouter

from backend.api import (
    dialogue,
    goals,
    graph,
    health,
    learning,
    paths,
    profile,
    resources,
    settings,
    students,
)


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(students.router)
api_router.include_router(goals.router)
api_router.include_router(paths.router)
api_router.include_router(learning.router)
api_router.include_router(dialogue.router)
api_router.include_router(graph.router)
api_router.include_router(profile.router)
api_router.include_router(resources.router)
api_router.include_router(settings.router)
