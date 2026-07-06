from threading import Lock
from typing import Any

from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import DriverError, Neo4jError

from backend.graph.config import Neo4jSettings
from backend.graph.demo_data import CANDIDATE_PATHS, DEMO_DATASET
from backend.utils.errors import AppError, NotFoundError


class Neo4jUnavailableError(AppError):
    def __init__(self, detail: str) -> None:
        super().__init__(f"Neo4j unavailable: {detail}", status_code=503)


class Neo4jGraphStore:
    def __init__(self, settings: Neo4jSettings) -> None:
        self.settings = settings
        try:
            self.driver = GraphDatabase.driver(
                settings.uri,
                auth=(settings.username, settings.password),
            )
        except (DriverError, Neo4jError, ValueError) as exc:
            raise Neo4jUnavailableError(str(exc)) from exc

    @classmethod
    def from_env(cls) -> "Neo4jGraphStore":
        return cls(Neo4jSettings.from_env())

    def close(self) -> None:
        self.driver.close()

    def verify_connectivity(self) -> None:
        try:
            self.driver.verify_connectivity(database=self.settings.database)
        except (DriverError, Neo4jError) as exc:
            raise Neo4jUnavailableError(str(exc)) from exc

    def read(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict]:
        return self._execute(query, parameters, RoutingControl.READ)

    def write(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict]:
        return self._execute(query, parameters, RoutingControl.WRITE)

    def _execute(
        self,
        query: str,
        parameters: dict[str, Any] | None,
        routing: RoutingControl,
    ) -> list[dict]:
        try:
            records, _, _ = self.driver.execute_query(
                query,
                parameters_=parameters or {},
                database_=self.settings.database,
                routing_=routing,
            )
            return [record.data() for record in records]
        except (DriverError, Neo4jError) as exc:
            raise Neo4jUnavailableError(str(exc)) from exc

    def get_full_graph(self) -> dict:
        nodes = self.read(
            """
            MATCH (node:KnowledgeNode {dataset: $dataset})
            WITH node ORDER BY node.id
            RETURN properties(node) AS node
            """,
            {"dataset": DEMO_DATASET},
        )
        edges = self.read(
            """
            MATCH (source:KnowledgeNode {dataset: $dataset})
                  -[relationship:PREREQUISITE|EXAMPLE_SUPPORT]->
                  (target:KnowledgeNode {dataset: $dataset})
            RETURN source.id AS source, target.id AS target, type(relationship) AS relation
            ORDER BY source, target, relation
            """,
            {"dataset": DEMO_DATASET},
        )
        return {
            "nodes": [item["node"] for item in nodes],
            "edges": edges,
        }

    def get_node(self, node_id: str) -> dict:
        rows = self.read(
            """
            MATCH (node:KnowledgeNode {id: $node_id, dataset: $dataset})
            RETURN properties(node) AS node
            """,
            {"node_id": node_id, "dataset": DEMO_DATASET},
        )
        if not rows:
            raise NotFoundError(f"Knowledge node not found in Neo4j: {node_id}")
        return rows[0]["node"]

    def get_prerequisites(self, node_id: str) -> list[dict]:
        rows = self.read(
            """
            MATCH (prerequisite:KnowledgeNode {dataset: $dataset})
                  -[:PREREQUISITE]->
                  (:KnowledgeNode {id: $node_id, dataset: $dataset})
            WITH prerequisite ORDER BY prerequisite.id
            RETURN properties(prerequisite) AS node
            """,
            {"node_id": node_id, "dataset": DEMO_DATASET},
        )
        return [item["node"] for item in rows]

    def get_successors(self, node_id: str) -> list[dict]:
        rows = self.read(
            """
            MATCH (:KnowledgeNode {id: $node_id, dataset: $dataset})
                  -[:PREREQUISITE]->
                  (successor:KnowledgeNode {dataset: $dataset})
            WITH successor ORDER BY successor.id
            RETURN properties(successor) AS node
            """,
            {"node_id": node_id, "dataset": DEMO_DATASET},
        )
        return [item["node"] for item in rows]

    def get_resources(self, node_id: str) -> list[dict]:
        rows = self.read(
            """
            MATCH (:KnowledgeNode {id: $node_id, dataset: $dataset})
                  -[:HAS_RESOURCE]->
                  (resource:LearningResource {dataset: $dataset})
            WITH resource ORDER BY resource.id
            RETURN properties(resource) AS resource
            """,
            {"node_id": node_id, "dataset": DEMO_DATASET},
        )
        return [item["resource"] for item in rows]

    def get_goal_target(self, goal_id: str) -> dict:
        rows = self.read(
            """
            MATCH (:LearningGoal {id: $goal_id, dataset: $dataset})
                  -[:TARGET_OF]->
                  (target:KnowledgeNode {dataset: $dataset})
            RETURN properties(target) AS node
            """,
            {"goal_id": goal_id, "dataset": DEMO_DATASET},
        )
        if not rows:
            raise NotFoundError(f"Learning goal not found in Neo4j: {goal_id}")
        return rows[0]["node"]

    def get_candidate_paths(self, goal_id: str) -> list[dict]:
        self.get_goal_target(goal_id)
        return CANDIDATE_PATHS

    def get_remedial_nodes(self, node_id: str) -> list[dict]:
        return self.get_prerequisites(node_id)


_store: Neo4jGraphStore | None = None
_store_lock = Lock()


def get_neo4j_store() -> Neo4jGraphStore:
    global _store
    if _store is None:
        with _store_lock:
            if _store is None:
                _store = Neo4jGraphStore.from_env()
    return _store


def close_neo4j_store() -> None:
    global _store
    with _store_lock:
        if _store is not None:
            _store.close()
            _store = None
