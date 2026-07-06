from backend.graph.demo_data import (
    DEMO_DATASET,
    EXAMPLE_SUPPORT_RELATIONSHIPS,
    KNOWLEDGE_NODES,
    LEARNING_GOAL,
    LEARNING_RESOURCES,
    PREREQUISITE_RELATIONSHIPS,
)
from backend.graph.store import Neo4jGraphStore


CONSTRAINTS = (
    "CREATE CONSTRAINT knowledge_node_id IF NOT EXISTS FOR (node:KnowledgeNode) REQUIRE node.id IS UNIQUE",
    "CREATE CONSTRAINT learning_goal_id IF NOT EXISTS FOR (goal:LearningGoal) REQUIRE goal.id IS UNIQUE",
    "CREATE CONSTRAINT learning_resource_id IF NOT EXISTS FOR (resource:LearningResource) REQUIRE resource.id IS UNIQUE",
)


def initialize_demo_graph(store: Neo4jGraphStore) -> dict[str, int]:
    store.verify_connectivity()

    store.write(
        "MATCH (node {dataset: $dataset}) DETACH DELETE node",
        {"dataset": DEMO_DATASET},
    )
    for constraint in CONSTRAINTS:
        store.write(constraint)

    nodes = [{**node, "dataset": DEMO_DATASET} for node in KNOWLEDGE_NODES]
    store.write(
        """
        UNWIND $nodes AS item
        CREATE (node:KnowledgeNode)
        SET node = item
        """,
        {"nodes": nodes},
    )

    store.write(
        """
        CREATE (goal:LearningGoal {
            id: $goal.id,
            title: $goal.title,
            description: $goal.description,
            dataset: $dataset
        })
        """,
        {"goal": LEARNING_GOAL, "dataset": DEMO_DATASET},
    )

    resources = [{**resource, "dataset": DEMO_DATASET} for resource in LEARNING_RESOURCES]
    store.write(
        """
        UNWIND $resources AS item
        CREATE (resource:LearningResource {
            id: item.id,
            title: item.title,
            resource_type: item.resource_type,
            content: item.content,
            url: item.url,
            difficulty: item.difficulty,
            dataset: item.dataset
        })
        WITH item, resource
        MATCH (node:KnowledgeNode {id: item.node_id})
        CREATE (node)-[:HAS_RESOURCE]->(resource)
        """,
        {"resources": resources},
    )

    store.write(
        """
        UNWIND $relationships AS item
        MATCH (source:KnowledgeNode {id: item.source})
        MATCH (target:KnowledgeNode {id: item.target})
        CREATE (source)-[:PREREQUISITE]->(target)
        """,
        {
            "relationships": [
                {"source": source, "target": target}
                for source, target in PREREQUISITE_RELATIONSHIPS
            ]
        },
    )
    store.write(
        """
        UNWIND $relationships AS item
        MATCH (source:KnowledgeNode {id: item.source})
        MATCH (target:KnowledgeNode {id: item.target})
        CREATE (source)-[:EXAMPLE_SUPPORT]->(target)
        """,
        {
            "relationships": [
                {"source": source, "target": target}
                for source, target in EXAMPLE_SUPPORT_RELATIONSHIPS
            ]
        },
    )
    store.write(
        """
        MATCH (goal:LearningGoal {id: $goal_id})
        MATCH (target:KnowledgeNode {id: $target_node_id})
        CREATE (goal)-[:TARGET_OF]->(target)
        """,
        {
            "goal_id": LEARNING_GOAL["id"],
            "target_node_id": LEARNING_GOAL["target_node_id"],
        },
    )

    counts = store.read(
        """
        MATCH (node:KnowledgeNode {dataset: $dataset})
        WITH count(node) AS knowledge_nodes
        MATCH (goal:LearningGoal {dataset: $dataset})
        WITH knowledge_nodes, count(goal) AS learning_goals
        MATCH (resource:LearningResource {dataset: $dataset})
        WITH knowledge_nodes, learning_goals, count(resource) AS resources
        MATCH (source {dataset: $dataset})-[relationship]->()
        RETURN knowledge_nodes, learning_goals, resources,
               count(relationship) AS relationships
        """,
        {"dataset": DEMO_DATASET},
    )[0]

    expected_relationships = (
        len(PREREQUISITE_RELATIONSHIPS)
        + len(EXAMPLE_SUPPORT_RELATIONSHIPS)
        + len(LEARNING_RESOURCES)
        + 1
    )
    expected = {
        "knowledge_nodes": len(KNOWLEDGE_NODES),
        "learning_goals": 1,
        "resources": len(LEARNING_RESOURCES),
        "relationships": expected_relationships,
    }
    if counts != expected:
        raise RuntimeError(f"Neo4j demo graph validation failed: {counts} != {expected}")
    return counts
