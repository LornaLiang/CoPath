import logging
from typing import Annotated, Any

from fastapi import APIRouter, Path

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import CodeApiResponse, code_response
from backend.schemas.requests import (
    PathEvaluateSwitchRequest,
    PathPlanRequest,
    PathSuggestionDecisionRequest,
    PathSuggestionRequest,
)
from backend.services.path_collaboration_service import PathCollaborationService
from backend.services.path_planner import PathPlanner
from backend.utils.errors import ConflictError


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/path", tags=["path-planning"])
StudentPathId = Annotated[str, Path(min_length=1, max_length=64)]


@router.post("/generate", response_model=CodeApiResponse[dict[str, Any]])
def generate_path(payload: PathPlanRequest, session: DatabaseSession) -> dict:
    return code_response(
        PathPlanner.generate_path(
            session,
            payload.student_id,
            payload.goal_id,
        )
    )


@router.post("/update", response_model=CodeApiResponse[dict[str, Any]])
def update_path(payload: PathPlanRequest, session: DatabaseSession) -> dict:
    raise ConflictError(
        "Direct path update is disabled. Use suggest-adjustment and "
        "confirm-adjustment for human-confirmed path changes."
    )


@router.post("/suggest-adjustment", response_model=CodeApiResponse[dict[str, Any] | None])
def suggest_adjustment(
    payload: PathSuggestionRequest,
    session: DatabaseSession,
) -> dict:
    return code_response(
        PathCollaborationService.suggest_adjustment(
            session,
            payload.student_id,
            payload.goal_id,
            trigger_type=payload.trigger_type,
            trigger_signal=payload.trigger_signal,
        )
    )


@router.post("/confirm-adjustment", response_model=CodeApiResponse[dict[str, Any]])
def confirm_adjustment(
    payload: PathSuggestionDecisionRequest,
    session: DatabaseSession,
) -> dict:
    return code_response(
        PathCollaborationService.confirm_adjustment(
            session,
            payload.student_id,
            payload.suggestion_id,
        )
    )


@router.post("/reject-adjustment", response_model=CodeApiResponse[dict[str, Any]])
def reject_adjustment(
    payload: PathSuggestionDecisionRequest,
    session: DatabaseSession,
) -> dict:
    return code_response(
        PathCollaborationService.reject_adjustment(
            session,
            payload.student_id,
            payload.suggestion_id,
        )
    )


@router.post("/evaluate-switch", response_model=CodeApiResponse[dict[str, Any]])
def evaluate_switch(
    payload: PathEvaluateSwitchRequest,
    session: DatabaseSession,
) -> dict:
    return code_response(
        PathCollaborationService.evaluate_switch(
            session,
            payload.student_id,
            payload.new_path_id,
            force=payload.force,
        )
    )


@router.get("/pending-adjustment/{student_id}", response_model=CodeApiResponse[dict[str, Any] | None])
def get_pending_adjustment(student_id: StudentPathId, session: DatabaseSession) -> dict:
    return code_response(
        PathCollaborationService.get_pending_adjustment(session, student_id)
    )


@router.get("/{student_id}", response_model=CodeApiResponse[dict[str, Any]])
def get_path(student_id: StudentPathId, session: DatabaseSession) -> dict:
    return code_response(PathPlanner.get_current_plan(session, student_id))
