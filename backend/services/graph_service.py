from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from backend.models import KnowledgeEdge, KnowledgeNode, LearningResource
from backend.services.common import require_node, require_student, serialize_resource
from backend.services.path_service import PathService


class GraphService:
    @staticmethod
    def get_graph(session: Session, student_id: str) -> dict:
        require_student(session, student_id)
        path = PathService.get_current_model(session, student_id)
        path_nodes = PathService.serialize_nodes(session, path, include_progress=True)
        statuses = {node["node_id"]: node["status"] for node in path_nodes}
        nodes = session.scalars(select(KnowledgeNode).order_by(KnowledgeNode.node_id)).all()
        edges = session.scalars(select(KnowledgeEdge).order_by(KnowledgeEdge.edge_id)).all()

        # TODO(Milestone 6): build and analyze the graph with NetworkX.
        return {
            "nodes": [
                {
                    "id": node.node_id,
                    "name": node.name,
                    "difficulty": node.difficulty,
                    "status": statuses.get(node.node_id, "not_in_path"),
                }
                for node in nodes
            ],
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "relation": edge.relation,
                }
                for edge in edges
            ],
            "current_path_nodes": PathService.get_node_ids(path),
            "current_node": PathService.get_current_node_id(session, path),
        }

    @staticmethod
    def get_node_detail(session: Session, node_id: str) -> dict:
        node = require_node(session, node_id)
        prerequisite_node = aliased(KnowledgeNode)
        next_node = aliased(KnowledgeNode)

        prerequisites = session.execute(
            select(prerequisite_node.node_id, prerequisite_node.name)
            .join(
                KnowledgeEdge,
                KnowledgeEdge.source_id == prerequisite_node.node_id,
            )
            .where(KnowledgeEdge.target_id == node_id)
            .order_by(prerequisite_node.node_id)
        ).all()
        next_nodes = session.execute(
            select(next_node.node_id, next_node.name)
            .join(KnowledgeEdge, KnowledgeEdge.target_id == next_node.node_id)
            .where(KnowledgeEdge.source_id == node_id)
            .order_by(next_node.node_id)
        ).all()
        resources = session.scalars(
            select(LearningResource)
            .where(LearningResource.node_id == node_id)
            .order_by(LearningResource.resource_id)
        ).all()

        return {
            "node_id": node.node_id,
            "name": node.name,
            "description": node.description,
            "difficulty": node.difficulty,
            "chapter": node.chapter,
            "prerequisites": [
                {"node_id": item.node_id, "name": item.name}
                for item in prerequisites
            ],
            "next_nodes": [
                {"node_id": item.node_id, "name": item.name} for item in next_nodes
            ],
            "resources": [serialize_resource(resource) for resource in resources],
        }
