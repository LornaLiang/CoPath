from fastapi import FastAPI

from backend.api.exceptions import register_exception_handlers
from backend.api.router import api_router


app = FastAPI(
    title="CoPath API",
    description="CoPath adaptive learning path planning system API",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")
register_exception_handlers(app)
