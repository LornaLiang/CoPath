import json
import sqlite3
from pathlib import Path

from backend.database.connection import DATABASE_PATH, PROJECT_ROOT, engine


SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
SEED_PATH = PROJECT_ROOT / "database" / "seed_data.sql"

TABLE_NAMES = (
    "students",
    "student_profiles",
    "knowledge_nodes",
    "knowledge_edges",
    "learning_goals",
    "learning_paths",
    "learning_events",
    "dialogue_logs",
    "path_switch_logs",
    "learning_resources",
    "system_settings",
)

MINIMUM_DEMO_COUNTS = {
    "students": 3,
    "knowledge_nodes": 12,
    "knowledge_edges": 15,
    "learning_goals": 1,
    "learning_paths": 3,
    "path_switch_logs": 1,
}


def _read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def get_table_counts(connection: sqlite3.Connection) -> dict[str, int]:
    return {
        table_name: connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]
        for table_name in TABLE_NAMES
    }


def _validate_demo_data(table_counts: dict[str, int]) -> None:
    missing = {
        table_name: minimum
        for table_name, minimum in MINIMUM_DEMO_COUNTS.items()
        if table_counts[table_name] < minimum
    }
    if missing:
        details = ", ".join(
            f"{table_name}>={minimum}" for table_name, minimum in missing.items()
        )
        raise RuntimeError(f"Demo data validation failed: {details}")


def initialize_database(database_path: Path = DATABASE_PATH) -> dict[str, int]:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(_read_sql(SCHEMA_PATH))
        connection.executescript(_read_sql(SEED_PATH))
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_errors:
            raise RuntimeError(f"Foreign key validation failed: {foreign_key_errors}")

        table_counts = get_table_counts(connection)
        _validate_demo_data(table_counts)

    return table_counts


def ensure_profile_schema(database_path: Path = DATABASE_PATH) -> bool:
    """Add mastery_json to pre-Milestone-8 databases without dropping data."""
    if not database_path.exists():
        return False

    if database_path == DATABASE_PATH:
        engine.dispose()
    changed = False
    with sqlite3.connect(database_path) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(student_profiles)")
        }
        if not columns:
            return False
        if "mastery_json" not in columns:
            connection.execute(
                "ALTER TABLE student_profiles "
                "ADD COLUMN mastery_json TEXT NOT NULL DEFAULT '{}'"
            )
            changed = True

        rows = connection.execute(
            "SELECT profile_id, profile_json, mastery_json FROM student_profiles"
        ).fetchall()
        for profile_id, profile_json, mastery_json in rows:
            if mastery_json and mastery_json != "{}":
                continue
            profile_data = json.loads(profile_json)
            mastery = profile_data.get("mastery", {})
            connection.execute(
                "UPDATE student_profiles SET mastery_json = ? WHERE profile_id = ?",
                (json.dumps(mastery, ensure_ascii=False), profile_id),
            )
            changed = True
        connection.commit()
    return changed


def reset_database(database_path: Path = DATABASE_PATH) -> dict[str, int]:
    engine.dispose()

    if database_path.exists():
        with sqlite3.connect(database_path) as connection:
            connection.execute("PRAGMA foreign_keys = OFF")
            for table_name in reversed(TABLE_NAMES):
                connection.execute(f"DROP TABLE IF EXISTS {table_name}")
            connection.commit()

    return initialize_database(database_path)
