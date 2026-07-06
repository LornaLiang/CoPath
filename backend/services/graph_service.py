from copy import deepcopy

from sqlalchemy.orm import Session

from backend.graph import get_neo4j_store
from backend.services.common import require_student
from backend.services.path_service import PathService


# SQLite Milestone 2 demo data uses the older identifier ``recursion``.  The
# Neo4j graph follows knowledge_graph_spec.md and calls the same concept
# ``recursion_thinking``.  Keep the business database unchanged and translate
# only at the GraphService boundary.
SQLITE_TO_GRAPH_NODE_IDS = {"recursion": "recursion_thinking"}
SQLITE_TO_GRAPH_GOAL_IDS = {"G001": "goal_recursion"}


def _graph_node_id(node_id: str) -> str:
    return SQLITE_TO_GRAPH_NODE_IDS.get(node_id, node_id)


def _graph_goal_id(goal_id: str) -> str:
    return SQLITE_TO_GRAPH_GOAL_IDS.get(goal_id, goal_id)


def _public_node(node: dict) -> dict:
    return {key: value for key, value in node.items() if key != "dataset"}


class GraphService:
    """The single business-facing entry point for Neo4j graph queries."""

    @staticmethod
    def get_full_graph() -> dict:
        graph = get_neo4j_store().get_full_graph()
        return {
            "nodes": [_public_node(node) for node in graph["nodes"]],
            "edges": [
                {
                    "source": edge["source"],
                    "target": edge["target"],
                    "relation": edge["relation"].lower(),
                }
                for edge in graph["edges"]
            ],
        }

    @staticmethod
    def get_graph(session: Session, student_id: str) -> dict:
        require_student(session, student_id)
        path = PathService.get_current_model(session, student_id)
        path_nodes = PathService.serialize_nodes(session, path, include_progress=True)
        statuses = {
            _graph_node_id(node["node_id"]): node["status"] for node in path_nodes
        }
        current_path_nodes = [
            _graph_node_id(node_id) for node_id in PathService.get_node_ids(path)
        ]
        current_node = _graph_node_id(PathService.get_current_node_id(session, path))
        graph = GraphService.get_full_graph()

        return {
            "nodes": [
                {
                    "id": node["id"],
                    "name": node["name"],
                    "difficulty": node["difficulty"],
                    "status": statuses.get(node["id"], "not_in_path"),
                }
                for node in graph["nodes"]
            ],
            "edges": graph["edges"],
            "current_path_nodes": current_path_nodes,
            "current_node": current_node,
        }

    @staticmethod
    def get_node_detail(node_id: str) -> dict:
        graph_node_id = _graph_node_id(node_id)
        store = get_neo4j_store()
        node = _public_node(store.get_node(graph_node_id))
        prerequisites = GraphService.get_prerequisites(graph_node_id)
        successors = GraphService.get_successors(graph_node_id)
        resources = GraphService.get_resources(graph_node_id)

        return {
            "node_id": node["id"],
            "name": node["name"],
            "description": node.get("description", ""),
            "difficulty": node["difficulty"],
            "chapter": node.get("chapter", ""),
            "prerequisites": [
                {"node_id": item["id"], "name": item["name"]}
                for item in prerequisites
            ],
            "next_nodes": [
                {"node_id": item["id"], "name": item["name"]}
                for item in successors
            ],
            "resources": resources,
        }

    @staticmethod
    def get_prerequisites(node_id: str) -> list[dict]:
        nodes = get_neo4j_store().get_prerequisites(_graph_node_id(node_id))
        return [_public_node(node) for node in nodes]

    @staticmethod
    def get_successors(node_id: str) -> list[dict]:
        nodes = get_neo4j_store().get_successors(_graph_node_id(node_id))
        return [_public_node(node) for node in nodes]

    @staticmethod
    def get_resources(node_id: str) -> list[dict]:
        resources = get_neo4j_store().get_resources(_graph_node_id(node_id))
        return [
            {
                "resource_id": resource["id"],
                "title": resource["title"],
                "resource_type": resource["resource_type"],
                "url": resource.get("url", ""),
                "content": resource.get("content", ""),
                "difficulty": resource["difficulty"],
            }
            for resource in resources
        ]

    @staticmethod
    def get_goal_target(goal_id: str) -> dict:
        node = get_neo4j_store().get_goal_target(_graph_goal_id(goal_id))
        return _public_node(node)

    @staticmethod
    def get_candidate_paths(goal_id: str) -> list[dict]:
        paths = get_neo4j_store().get_candidate_paths(_graph_goal_id(goal_id))
        return deepcopy(paths)

    @staticmethod
    def get_remedial_nodes(node_id: str) -> list[dict]:
        nodes = get_neo4j_store().get_remedial_nodes(_graph_node_id(node_id))
        return [_public_node(node) for node in nodes]
