"""CoPath SQLAlchemy model registry."""

from backend.models.activity import DialogueLog, PathSwitchLog
from backend.models.knowledge import (
    KnowledgeEdge,
    KnowledgeNode,
    LearningGoal,
    LearningResource,
)
from backend.models.learning import LearningEvent, LearningPath
from backend.models.setting import SystemSetting
from backend.models.student import Student, StudentProfile

__all__ = [
    "DialogueLog",
    "KnowledgeEdge",
    "KnowledgeNode",
    "LearningEvent",
    "LearningGoal",
    "LearningPath",
    "LearningResource",
    "PathSwitchLog",
    "Student",
    "StudentProfile",
    "SystemSetting",
]
