import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

from backend.database.connection import PROJECT_ROOT
from backend.utils.errors import AppError


class Neo4jConfigurationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=503)


@dataclass(frozen=True)
class Neo4jSettings:
    uri: str
    username: str
    password: str = field(repr=False)
    database: str = "neo4j"

    @classmethod
    def from_env(cls) -> "Neo4jSettings":
        load_dotenv(PROJECT_ROOT / ".env", override=False)
        values = {
            "uri": os.getenv("NEO4J_URI"),
            "username": os.getenv("NEO4J_USERNAME"),
            "password": os.getenv("NEO4J_PASSWORD"),
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            variable_names = ", ".join(f"NEO4J_{name.upper()}" for name in missing)
            raise Neo4jConfigurationError(
                f"Neo4j is not configured. Missing environment variables: {variable_names}"
            )
        return cls(
            uri=values["uri"],
            username=values["username"],
            password=values["password"],
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
        )
