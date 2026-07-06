import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from backend.utils.errors import AppError


logger = logging.getLogger(__name__)


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "data": None,
            "message": message,
        },
    )


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "API request rejected method=%s path=%s status=%s message=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.message,
    )
    return error_response(exc.status_code, exc.message)


async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else None
    if first_error:
        location = ".".join(str(item) for item in first_error["loc"])
        message = f"Invalid request parameter {location}: {first_error['msg']}"
    else:
        message = "Invalid request parameters"
    logger.warning(
        "API validation failed method=%s path=%s message=%s",
        request.method,
        request.url.path,
        message,
    )
    return error_response(422, message)


async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        "HTTP request failed method=%s path=%s status=%s message=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return error_response(exc.status_code, str(exc.detail))


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled API error method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return error_response(500, "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(HTTPException, handle_http_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
