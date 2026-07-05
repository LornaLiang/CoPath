from typing import Any

from fastapi import APIRouter

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.schemas.requests import StudentSwitchRequest
from backend.services.settings_service import SettingsService


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=ApiResponse[dict[str, Any]])
def get_settings(session: DatabaseSession) -> dict:
    return success_response(SettingsService.get_settings(session))


@router.post("/student", response_model=ApiResponse[dict[str, Any]])
def switch_student(payload: StudentSwitchRequest, session: DatabaseSession) -> dict:
    return success_response(
        SettingsService.switch_student(session, payload.student_id)
    )


@router.post("/reset-demo", response_model=ApiResponse[dict[str, Any]])
def reset_demo() -> dict:
    data = SettingsService.reset_demo()
    return success_response(data, message=data["message"])
