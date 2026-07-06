from typing import Annotated, Any

from fastapi import APIRouter, Path, Query

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import (
    ApiResponse,
    CodeApiResponse,
    code_response,
    success_response,
)
from backend.schemas.requests import ProfileEventRequest, ProfileUpdateRequest
from backend.services.profile_service import LearningProfileService, ProfileService


router = APIRouter(prefix="/profile", tags=["profile"])
StudentId = Annotated[str, Query(min_length=1, max_length=64)]
StudentPathId = Annotated[str, Path(min_length=1, max_length=64)]


@router.get("", response_model=ApiResponse[dict[str, Any]])
def get_profile(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(ProfileService.get_profile(session, student_id))


@router.get("/mastery", response_model=ApiResponse[list[dict[str, Any]]])
def get_mastery(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(ProfileService.get_mastery(session, student_id))


@router.post("/update", response_model=CodeApiResponse[dict[str, Any]])
def update_profile(payload: ProfileUpdateRequest, session: DatabaseSession) -> dict:
    return code_response(
        LearningProfileService.apply_ai_signal(
            session,
            payload.student_id,
            payload.ai_signal.model_dump(mode="json"),
        )
    )


@router.post("/event", response_model=CodeApiResponse[dict[str, Any]])
def update_profile_from_event(
    payload: ProfileEventRequest,
    session: DatabaseSession,
) -> dict:
    return code_response(
        LearningProfileService.record_profile_event(
            session,
            payload.student_id,
            payload.node_id,
            payload.result,
        )
    )


@router.get("/{student_id}", response_model=CodeApiResponse[dict[str, Any]])
def get_profile_by_id(student_id: StudentPathId, session: DatabaseSession) -> dict:
    return code_response(
        LearningProfileService.get_profile_snapshot(session, student_id)
    )
