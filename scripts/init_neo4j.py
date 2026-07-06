import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.graph.initializer import initialize_demo_graph  # noqa: E402
from backend.graph.store import Neo4jGraphStore  # noqa: E402
from backend.utils.errors import AppError  # noqa: E402


def main() -> None:
    store = None
    try:
        store = Neo4jGraphStore.from_env()
        counts = initialize_demo_graph(store)
    except AppError as exc:
        raise SystemExit(f"Neo4j initialization failed: {exc.message}") from exc
    except RuntimeError as exc:
        raise SystemExit(f"Neo4j initialization failed: {exc}") from exc
    finally:
        if store is not None:
            store.close()

    print("Neo4j demo graph initialized successfully.")
    print(f"Inserted knowledge nodes: {counts['knowledge_nodes']}")
    print(f"Inserted learning goals: {counts['learning_goals']}")
    print(f"Inserted resources: {counts['resources']}")
    print(f"Inserted relationships: {counts['relationships']}")


if __name__ == "__main__":
    main()
