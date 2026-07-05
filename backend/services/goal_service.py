from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import LearningGoal
from backend.services.common import require_student
from backend.services.path_service import PathService
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
        return {
            "goal_id": goal.goal_id,
            "target_node_id": goal.target_node_id,
            "candidate_paths": candidate_paths,
            "current_path": current_path,
        }
