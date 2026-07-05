from typing import Annotated, Any

from fastapi import APIRouter, Query

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.services.resource_service import ResourceService


router = APIRouter(prefix="/resources", tags=["resources"])
StudentId = Annotated[str, Query(min_length=1, max_length=64)]


@router.get("/current", response_model=ApiResponse[list[dict[str, Any]]])
def get_current_resources(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(ResourceService.get_current_resources(session, student_id))
