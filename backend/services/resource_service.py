from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import LearningResource
from backend.services.common import serialize_resource
from backend.services.path_service import PathService


class ResourceService:
    @staticmethod
    def get_current_resources(session: Session, student_id: str) -> list[dict]:
        path = PathService.get_current_model(session, student_id)
        current_node_id = PathService.get_current_node_id(session, path)
        resources = session.scalars(
            select(LearningResource)
            .where(LearningResource.node_id == current_node_id)
            .order_by(LearningResource.resource_id)
        ).all()
        return [serialize_resource(resource) for resource in resources]
