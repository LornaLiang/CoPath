from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import KnowledgeNode, LearningGoal, StudentProfile
from backend.services.common import require_student
from backend.services.path_service import PathService
from backend.utils.errors import NotFoundError
from backend.utils.json import parse_json


class ProfileService:
    @staticmethod
    def get_profile(session: Session, student_id: str) -> dict:
        student = require_student(session, student_id)
        profile = session.scalar(
            select(StudentProfile).where(StudentProfile.student_id == student_id)
        )
        if profile is None:
            raise NotFoundError(f"Learning profile not found: {student_id}")

        profile_data = parse_json(profile.profile_json, "student_profiles.profile_json")
        goal = (
            session.get(LearningGoal, student.current_goal_id)
            if student.current_goal_id
            else None
        )
        path = PathService.get_current_model(session, student_id)
        weak_node_ids = profile_data.get("weak_points", [])
        weak_nodes = session.scalars(
            select(KnowledgeNode).where(KnowledgeNode.node_id.in_(weak_node_ids))
        ).all()
        names_by_id = {node.node_id: node.name for node in weak_nodes}

        return {
            "student_id": student_id,
            "learning_speed": profile.learning_speed,
            "learning_preference": profile.learning_preference,
            "confidence": profile.confidence,
            "current_goal": goal.title if goal else None,
            "current_path": path.path_name,
            "weak_points": [
                names_by_id[node_id]
                for node_id in weak_node_ids
                if node_id in names_by_id
            ],
            "recent_state": profile_data.get("recent_state"),
        }

    @staticmethod
    def get_mastery(session: Session, student_id: str) -> list[dict]:
        require_student(session, student_id)
        profile = session.scalar(
            select(StudentProfile).where(StudentProfile.student_id == student_id)
        )
        if profile is None:
            raise NotFoundError(f"Learning profile not found: {student_id}")

        profile_data = parse_json(profile.profile_json, "student_profiles.profile_json")
        mastery = profile_data.get("mastery", {})
        nodes = session.scalars(
            select(KnowledgeNode).where(KnowledgeNode.node_id.in_(mastery.keys()))
        ).all()
        nodes_by_id = {node.node_id: node for node in nodes}
        return [
            {
                "node_id": node_id,
                "name": nodes_by_id[node_id].name,
                "mastery": value,
            }
            for node_id, value in mastery.items()
            if node_id in nodes_by_id
        ]
