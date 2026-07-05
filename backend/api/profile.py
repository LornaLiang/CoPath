from typing import Annotated, Any

from fastapi import APIRouter, Query

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.services.profile_service import ProfileService


router = APIRouter(prefix="/profile", tags=["profile"])
StudentId = Annotated[str, Query(min_length=1, max_length=64)]


@router.get("", response_model=ApiResponse[dict[str, Any]])
def get_profile(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(ProfileService.get_profile(session, student_id))


@router.get("/mastery", response_model=ApiResponse[list[dict[str, Any]]])
def get_mastery(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(ProfileService.get_mastery(session, student_id))
