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
            # TODO(Milestone 7): report the configured AI provider's real status.
            "ai": "not_configured",
        }
