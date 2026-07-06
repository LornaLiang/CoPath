"""Neo4j knowledge graph storage."""

from backend.graph.store import close_neo4j_store, get_neo4j_store

__all__ = ["close_neo4j_store", "get_neo4j_store"]
