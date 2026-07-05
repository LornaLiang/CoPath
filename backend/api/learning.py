from typing import Annotated, Any

from fastapi import APIRouter, Query

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.schemas.requests import LearningEventRequest, LearningFeedbackRequest
from backend.services.learning_service import LearningService


router = APIRouter(prefix="/learning", tags=["learning"])
StudentId = Annotated[str, Query(min_length=1, max_length=64)]


@router.get("/current", response_model=ApiResponse[dict[str, Any]])
def get_current_learning(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(LearningService.get_current(session, student_id))


@router.post("/event", response_model=ApiResponse[dict[str, Any]])
def save_learning_event(
    payload: LearningEventRequest,
    session: DatabaseSession,
) -> dict:
    return success_response(
        LearningService.save_event(
            session,
            payload.student_id,
            payload.node_id,
            payload.event_type,
            payload.result,
            payload.score,
            payload.time_spent,
        )
    )


@router.post("/feedback", response_model=ApiResponse[dict[str, Any]])
def submit_learning_feedback(
    payload: LearningFeedbackRequest,
    session: DatabaseSession,
) -> dict:
    return success_response(
        LearningService.accept_feedback(
            session,
            payload.student_id,
            payload.node_id,
            payload.feedback_type,
        )
    )


@router.get("/events", response_model=ApiResponse[list[dict[str, Any]]])
def list_learning_events(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(LearningService.list_events(session, student_id))


@router.get("/summary", response_model=ApiResponse[dict[str, Any]])
def get_learning_summary(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(LearningService.get_summary(session, student_id))
