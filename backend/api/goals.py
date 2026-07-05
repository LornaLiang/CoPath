from typing import Any

from fastapi import APIRouter

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.schemas.requests import GoalSelectRequest
from backend.services.goal_service import GoalService


router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=ApiResponse[list[dict[str, Any]]])
def list_goals(session: DatabaseSession) -> dict:
    return success_response(GoalService.list_goals(session))


@router.post("/select", response_model=ApiResponse[dict[str, Any]])
def select_goal(payload: GoalSelectRequest, session: DatabaseSession) -> dict:
    return success_response(
        GoalService.select_goal(session, payload.student_id, payload.goal_id)
    )
