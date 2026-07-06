from backend.ai.config import AISettings
from backend.database.connection import check_database_connection


class HealthService:
    """Provide infrastructure status without exposing database access to routes."""

    @staticmethod
    def get_health() -> dict[str, str]:
        return {
            "status": "running",
            "database": (
                "connected" if check_database_connection() else "disconnected"
            ),
            "ai": "available" if AISettings.is_configured() else "not_configured",
        }
