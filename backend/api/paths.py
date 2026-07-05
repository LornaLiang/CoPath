from typing import Annotated, Any

from fastapi import APIRouter, Query

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.schemas.requests import PathSwitchRequest
from backend.services.path_service import PathService


router = APIRouter(prefix="/paths", tags=["paths"])
Identifier = Annotated[str, Query(min_length=1, max_length=64)]


@router.get("/current", response_model=ApiResponse[dict[str, Any]])
def get_current_path(student_id: Identifier, session: DatabaseSession) -> dict:
    return success_response(PathService.get_current(session, student_id))


@router.get("/candidates", response_model=ApiResponse[list[dict[str, Any]]])
def list_candidate_paths(
    student_id: Identifier,
    goal_id: Identifier,
    session: DatabaseSession,
) -> dict:
    return success_response(PathService.list_candidates(session, student_id, goal_id))


@router.post("/switch", response_model=ApiResponse[dict[str, Any]])
def switch_path(payload: PathSwitchRequest, session: DatabaseSession) -> dict:
    return success_response(
        PathService.switch_path(
            session,
            payload.student_id,
            payload.new_path_id,
            payload.reason,
        )
    )


@router.get("/switch-logs", response_model=ApiResponse[list[dict[str, Any]]])
def list_switch_logs(student_id: Identifier, session: DatabaseSession) -> dict:
    return success_response(PathService.list_switch_logs(session, student_id))
