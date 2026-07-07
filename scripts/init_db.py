import json
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "demo.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
SEED_PATH = PROJECT_ROOT / "database" / "seed_data.sql"

TABLE_LABELS = {
    "students": "students",
    "student_profiles": "student profiles",
    "knowledge_nodes": "knowledge nodes",
    "knowledge_edges": "knowledge edges",
    "learning_goals": "learning goals",
    "learning_paths": "paths",
    "learning_events": "events",
    "dialogue_logs": "dialogues",
    "path_switch_logs": "path switch logs",
    "path_adjustment_suggestions": "path adjustment suggestions",
    "learning_resources": "resources",
    "system_settings": "system settings",
}

EXPECTED_COUNTS = {
    "students": 3,
    "student_profiles": 3,
    "knowledge_nodes": 12,
    "knowledge_edges": 15,
    "learning_goals": 1,
    "learning_paths": 9,
    "learning_events": 10,
    "dialogue_logs": 0,
    "path_switch_logs": 2,
    "path_adjustment_suggestions": 0,
    "learning_resources": 36,
    "system_settings": 6,
}

EXPECTED_COLUMNS = {
    "students": ("student_id", "name", "avatar", "current_goal_id", "created_at"),
    "student_profiles": (
        "profile_id",
        "student_id",
        "learning_speed",
        "learning_preference",
        "confidence",
        "mastery_json",
        "profile_json",
        "updated_at",
    ),
    "knowledge_nodes": (
        "node_id",
        "name",
        "description",
        "difficulty",
        "chapter",
    ),
    "knowledge_edges": (
        "edge_id",
        "source_id",
        "target_id",
        "relation",
    ),
    "learning_goals": (
        "goal_id",
        "target_node_id",
        "title",
        "description",
        "recommended_level",
    ),
    "learning_paths": (
        "path_id",
        "student_id",
        "goal_id",
        "path_type",
        "path_name",
        "nodes_json",
        "is_current",
        "status",
        "reason",
        "created_at",
    ),
    "learning_events": (
        "event_id",
        "student_id",
        "node_id",
        "event_type",
        "result",
        "score",
        "time_spent",
        "created_at",
    ),
    "dialogue_logs": (
        "dialogue_id",
        "student_id",
        "node_id",
        "user_message",
        "ai_response",
        "extracted_signal_json",
        "created_at",
    ),
    "path_switch_logs": (
        "switch_id",
        "student_id",
        "old_path_id",
        "new_path_id",
        "trigger_type",
        "trigger_signal_json",
        "reason",
        "created_at",
    ),
    "path_adjustment_suggestions": (
        "suggestion_id",
        "student_id",
        "current_path_id",
        "suggested_path_type",
        "suggested_nodes_json",
        "trigger_type",
        "trigger_signal_json",
        "reason",
        "risk_level",
        "status",
        "created_at",
        "confirmed_at",
    ),
    "learning_resources": (
        "resource_id",
        "node_id",
        "title",
        "resource_type",
        "url",
        "content",
        "difficulty",
    ),
    "system_settings": ("setting_key", "setting_value"),
}

JSON_FIELDS = (
    ("student_profiles", "mastery_json"),
    ("student_profiles", "profile_json"),
    ("learning_paths", "nodes_json"),
    ("dialogue_logs", "extracted_signal_json"),
    ("path_switch_logs", "trigger_signal_json"),
    ("path_adjustment_suggestions", "suggested_nodes_json"),
    ("path_adjustment_suggestions", "trigger_signal_json"),
)


def read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_database(connection: sqlite3.Connection) -> dict[str, int]:
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"database integrity check failed: {integrity}")

    foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_errors:
        raise RuntimeError(f"foreign key validation failed: {foreign_key_errors}")

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        actual_columns = tuple(
            row[1] for row in connection.execute(f"PRAGMA table_info({table_name})")
        )
        if actual_columns != expected_columns:
            raise RuntimeError(
                f"schema mismatch for {table_name}: "
                f"expected {expected_columns}, got {actual_columns}"
            )

    counts = {
        table_name: connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]
        for table_name in TABLE_LABELS
    }
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(
            f"unexpected demo row counts: expected {EXPECTED_COUNTS}, got {counts}"
        )

    parsed_json: dict[tuple[str, str], list] = {}
    for table_name, column_name in JSON_FIELDS:
        parsed_json[(table_name, column_name)] = []
        rows = connection.execute(f"SELECT {column_name} FROM {table_name}")
        for (value,) in rows:
            parsed_json[(table_name, column_name)].append(json.loads(value))

    knowledge_node_ids = {
        row[0] for row in connection.execute("SELECT node_id FROM knowledge_nodes")
    }
    for node_ids in parsed_json[("learning_paths", "nodes_json")]:
        unknown_node_ids = set(node_ids) - knowledge_node_ids
        if unknown_node_ids:
            raise RuntimeError(f"path references unknown nodes: {unknown_node_ids}")

    resource_coverage = connection.execute(
        """
        SELECT node_id, COUNT(*), GROUP_CONCAT(resource_type, ',')
        FROM learning_resources
        GROUP BY node_id
        ORDER BY node_id
        """
    ).fetchall()
    if len(resource_coverage) != 12:
        raise RuntimeError("not every knowledge node has learning resources")
    for node_id, count, resource_types in resource_coverage:
        if count != 3 or set(resource_types.split(",")) != {"text", "code", "exercise"}:
            raise RuntimeError(f"invalid resource coverage for {node_id}")

    current_paths = connection.execute(
        """
        SELECT student_id, COUNT(*)
        FROM learning_paths
        WHERE is_current = 1
        GROUP BY student_id
        ORDER BY student_id
        """
    ).fetchall()
    if current_paths != [("S001", 1), ("S002", 1), ("S003", 1)]:
        raise RuntimeError(f"invalid current paths: {current_paths}")

    return counts


def initialize_demo_database() -> dict[str, int]:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(read_sql(SCHEMA_PATH))
            connection.executescript(read_sql(SEED_PATH))
            return validate_database(connection)
    except Exception:
        DATABASE_PATH.unlink(missing_ok=True)
        raise


def main() -> None:
    counts = initialize_demo_database()
    for table_name, label in TABLE_LABELS.items():
        print(f"inserted {label}: {counts[table_name]}")
    print(f"database: {DATABASE_PATH}")
    print("demo database initialized successfully")


if __name__ == "__main__":
    main()
