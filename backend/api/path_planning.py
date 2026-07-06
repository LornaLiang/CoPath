import logging
from typing import Annotated, Any

from fastapi import APIRouter, Path

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import CodeApiResponse, code_response
from backend.schemas.requests import PathPlanRequest
from backend.services.path_planner import PathPlanner


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
    result = PathPlanner.update_path(
        session,
        payload.student_id,
        payload.goal_id,
    )
    logger.info(
        "Path update evaluated student_id=%s goal_id=%s selected_path=%s "
        "changed=%s adjustments=%s reason=%s",
        payload.student_id,
        payload.goal_id,
        result["selected_path"],
        result["changed"],
        len(result["adjustments"]),
        result["reason"],
    )
    return code_response(result)


@router.get("/{student_id}", response_model=CodeApiResponse[dict[str, Any]])
def get_path(student_id: StudentPathId, session: DatabaseSession) -> dict:
    return code_response(PathPlanner.get_current_plan(session, student_id))
