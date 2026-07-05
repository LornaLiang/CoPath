from typing import Annotated, Any

from fastapi import APIRouter, Path, Query

from backend.api.dependencies import DatabaseSession
from backend.schemas.common import ApiResponse, success_response
from backend.services.graph_service import GraphService


router = APIRouter(prefix="/graph", tags=["graph"])
StudentId = Annotated[str, Query(min_length=1, max_length=64)]
NodeId = Annotated[str, Path(min_length=1, max_length=64)]


@router.get("", response_model=ApiResponse[dict[str, Any]])
def get_graph(student_id: StudentId, session: DatabaseSession) -> dict:
    return success_response(GraphService.get_graph(session, student_id))


@router.get("/node/{node_id}", response_model=ApiResponse[dict[str, Any]])
def get_node_detail(node_id: NodeId, session: DatabaseSession) -> dict:
    return success_response(GraphService.get_node_detail(session, node_id))
