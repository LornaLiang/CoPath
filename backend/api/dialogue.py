from typing import Annotated, Any

from fastapi import APIRouter, Query

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.schemas.requests import ChatRequest
from backend.services.dialogue_service import DialogueService


router = APIRouter(tags=["dialogue"])
StudentId = Annotated[str, Query(min_length=1, max_length=64)]


@router.get("/dialogues", response_model=ApiResponse[list[dict[str, Any]]])
def list_dialogues(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(DialogueService.list_dialogues(session, student_id))


@router.post("/chat", response_model=ApiResponse[dict[str, Any]])
def chat(payload: ChatRequest, session: DatabaseSession) -> dict:
    return success_response(
        DialogueService.create_chat(
            session,
            payload.student_id,
            payload.node_id,
            payload.message,
        )
    )
