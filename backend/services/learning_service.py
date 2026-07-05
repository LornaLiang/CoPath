from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import (
    KnowledgeNode,
    LearningEvent,
    LearningResource,
    StudentProfile,
)
from backend.services.common import require_node, require_student, serialize_resource
from backend.services.path_service import PathService
from backend.utils.errors import NotFoundError
from backend.utils.json import parse_json


class LearningService:
    @staticmethod
    def get_current(session: Session, student_id: str) -> dict:
        path = PathService.get_current_model(session, student_id)
        node_ids = PathService.get_node_ids(path)
        current_node_id = PathService.get_current_node_id(session, path)
        node = require_node(session, current_node_id)
        current_index = node_ids.index(current_node_id)
        total = len(node_ids)
        resources = session.scalars(
            select(LearningResource)
            .where(LearningResource.node_id == current_node_id)
            .order_by(LearningResource.resource_id)
        ).all()

        return {
            "current_node": {
                "node_id": node.node_id,
                "name": node.name,
                "description": node.description,
            },
            "path_progress": {
                "completed": current_index,
                "total": total,
                "percent": round(current_index / total * 100) if total else 0,
            },
            "resources": [serialize_resource(resource) for resource in resources],
        }

    @staticmethod
    def save_event(
        session: Session,
        student_id: str,
        node_id: str,
        event_type: str,
        result: str | None,
        score: float | None,
        time_spent: int | None,
    ) -> dict:
        require_student(session, student_id)
        require_node(session, node_id)
        session.add(
            LearningEvent(
                student_id=student_id,
                node_id=node_id,
                event_type=event_type,
                result=result,
                score=score,
                time_spent=time_spent,
            )
        )
        session.commit()

        # TODO(Milestone 8): update the learning profile from this event.
        # TODO(Milestone 9): evaluate whether the path should be adjusted.
        return {
            "event_saved": True,
            "profile_updated": False,
            "path_adjusted": False,
            "new_path": None,
        }

    @staticmethod
    def accept_feedback(
        session: Session,
        student_id: str,
        node_id: str,
        feedback_type: str,
    ) -> dict:
        require_student(session, student_id)
        require_node(session, node_id)

        suggestions = {
            "understood": ("continue", "反馈已接收，可以继续当前学习路径。"),
            "still_confused": (
                "insert_prerequisite",
                "反馈已接收，路径调整将在后续里程碑启用。",
            ),
            "need_example": ("show_example", "反馈已接收，建议查看案例型学习资源。"),
            "lower_difficulty": (
                "switch_path",
                "反馈已接收，难度调整将在后续里程碑启用。",
            ),
            "next_node": ("next_node", "反馈已接收，节点推进将在后续里程碑启用。"),
        }
        suggested_action, message = suggestions[feedback_type]

        # TODO(Milestone 8/9): consume feedback in profile and adaptation services.
        return {
            "feedback_saved": True,
            "suggested_action": suggested_action,
            "message": message,
        }

    @staticmethod
    def list_events(session: Session, student_id: str) -> list[dict]:
        require_student(session, student_id)
        rows = session.execute(
            select(LearningEvent, KnowledgeNode.name)
            .join(KnowledgeNode, KnowledgeNode.node_id == LearningEvent.node_id)
            .where(LearningEvent.student_id == student_id)
            .order_by(LearningEvent.created_at.desc(), LearningEvent.event_id.desc())
        ).all()
        return [
            {
                "event_id": event.event_id,
                "node_name": node_name,
                "event_type": event.event_type,
                "result": event.result,
                "score": event.score,
                "time_spent": event.time_spent,
                "created_at": event.created_at,
            }
            for event, node_name in rows
        ]

    @staticmethod
    def get_summary(session: Session, student_id: str) -> dict:
        require_student(session, student_id)
        profile = session.scalar(
            select(StudentProfile).where(StudentProfile.student_id == student_id)
        )
        if profile is None:
            raise NotFoundError(f"Learning profile not found: {student_id}")

        profile_data = parse_json(profile.profile_json, "student_profiles.profile_json")
        weak_node_ids = profile_data.get("weak_points", [])
        weak_nodes = session.scalars(
            select(KnowledgeNode).where(KnowledgeNode.node_id.in_(weak_node_ids))
        ).all()
        names_by_id = {node.node_id: node.name for node in weak_nodes}
        weak_points = [
            names_by_id[node_id] for node_id in weak_node_ids if node_id in names_by_id
        ]
        path = PathService.get_current_model(session, student_id)

        weak_text = "、".join(weak_points) if weak_points else "暂无明显薄弱点"
        next_suggestion = (
            f"建议先复习{weak_points[0]}，再继续当前路径。"
            if weak_points
            else "建议继续当前学习路径。"
        )
        # TODO(Milestone 7): replace this deterministic summary with an AI summary.
        return {
            "summary": f"当前薄弱点为{weak_text}，正在采用{path.path_name}。",
            "weak_points": weak_points,
            "next_suggestion": next_suggestion,
        }
