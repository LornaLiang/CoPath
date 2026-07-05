from typing import Any

from fastapi import APIRouter

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.services.student_service import StudentService


router = APIRouter(prefix="/students", tags=["students"])


@router.get("/current", response_model=ApiResponse[dict[str, Any]])
def get_current_student(session: DatabaseSession) -> dict:
    return success_response(StudentService.get_current(session))


@router.get("", response_model=ApiResponse[list[dict[str, Any]]])
def list_students(session: DatabaseSession) -> dict:
    return success_response(StudentService.list_students(session))
