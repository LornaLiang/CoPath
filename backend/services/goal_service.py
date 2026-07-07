from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.ai import get_ai_service
from backend.ai.config import AIConfigurationError, AISettings
from backend.models import LearningGoal
from backend.services.common import require_student
from backend.services.path_service import PathService
from backend.services.profile_service import ProfileService
from backend.utils.errors import NotFoundError


class GoalService:
    @staticmethod
    def list_goals(session: Session) -> list[dict]:
        goals = session.scalars(select(LearningGoal).order_by(LearningGoal.goal_id)).all()
        return [
            {
                "goal_id": goal.goal_id,
                "title": goal.title,
                "target_node_id": goal.target_node_id,
                "description": goal.description,
                "recommended_level": goal.recommended_level,
            }
            for goal in goals
        ]

    @staticmethod
    def select_goal(session: Session, student_id: str, goal_id: str) -> dict:
        student = require_student(session, student_id)
        goal = session.get(LearningGoal, goal_id)
        if goal is None:
            raise NotFoundError(f"Learning goal not found: {goal_id}")

        student.current_goal_id = goal_id
        session.commit()

        # TODO(Milestone 9): generate and rank paths when no stored candidates exist.
        candidate_paths = PathService.list_candidates(session, student_id, goal_id)
        current_path = PathService.get_current(session, student_id)
        result = {
            "goal_id": goal.goal_id,
            "target_node_id": goal.target_node_id,
            "candidate_paths": candidate_paths,
            "current_path": current_path,
        }
        ai_recommendation = GoalService._mock_ai_recommendation(
            session,
            student,
            goal,
        )
        if ai_recommendation is not None:
            result["ai_recommendation"] = ai_recommendation
        return result

    @staticmethod
    def _mock_ai_recommendation(
        session: Session,
        student,
        goal: LearningGoal,
    ) -> dict | None:
        try:
            settings = AISettings.from_env()
        except AIConfigurationError:
            return None
        if settings.mode != "mock":
            return None

        profile = ProfileService.get_profile(session, student.student_id)
        result = get_ai_service().generate_reply(
            model="mock",
            context={
                "student": {"id": student.student_id, "name": student.name},
                "profile": profile,
                "current_node": {"id": goal.target_node_id},
            },
            message="请解释三条学习路径并推荐一条路径",
        )
        return result.model_dump(mode="json")
