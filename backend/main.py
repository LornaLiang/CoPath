from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.ai import close_ai_service
from backend.api.exceptions import register_exception_handlers
from backend.api.router import api_router
from backend.database.initializer import (
    ensure_path_collaboration_schema,
    ensure_profile_schema,
)
from backend.graph import close_neo4j_store


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_profile_schema()
    ensure_path_collaboration_schema()
    yield
    close_ai_service()
    close_neo4j_store()


app = FastAPI(
    title="CoPath API",
    description="CoPath adaptive learning path planning system API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")
register_exception_handlers(app)
