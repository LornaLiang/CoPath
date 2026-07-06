import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import (
    KnowledgeNode,
    LearningEvent,
    LearningGoal,
    Student,
    StudentProfile,
)
from backend.services.path_service import PathService
from backend.utils.errors import AppError, ConflictError, NotFoundError
from backend.utils.json import parse_json


MASTERY_DEFAULT = 0.5
CORRECT_MASTERY_DELTA = 0.08
CORRECT_CONFIDENCE_DELTA = 0.03
WRONG_MASTERY_DELTA = 0.05
WRONG_CONFIDENCE_DELTA = 0.05
GRAPH_TO_SQLITE_NODE_IDS = {"recursion_thinking": "recursion"}
logger = logging.getLogger(__name__)


def _clamp(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 4)


class LearningProfileService:
    """Maintain cumulative, deterministic learning profiles in SQLite."""

    @staticmethod
    def initialize_profile(
        session: Session,
        student_identifier: str,
        *,
        commit: bool = True,
    ) -> StudentProfile:
        student = LearningProfileService._resolve_student(session, student_identifier)
        profile = session.scalar(
            select(StudentProfile).where(
                StudentProfile.student_id == student.student_id
            )
        )
        if profile is not None:
            return profile

        profile = StudentProfile(
            student_id=student.student_id,
            learning_speed="medium",
            learning_preference="basic",
            confidence=0.5,
            mastery_json="{}",
            profile_json=json.dumps(
                {"mastery": {}, "weak_points": [], "recent_state": "focused"},
                ensure_ascii=False,
            ),
        )
        session.add(profile)
        LearningProfileService._finish(session, commit)
        return profile

    @staticmethod
    def get_profile(session: Session, student_identifier: str) -> dict:
        LearningProfileService.initialize_profile(
            session,
            student_identifier,
            commit=True,
        )
        student, profile, _, profile_data = (
            LearningProfileService._load_state(session, student_identifier)
        )
        return LearningProfileService._serialize_basic_profile(
            session,
            student,
            profile,
            profile_data,
        )

    @staticmethod
    def get_profile_snapshot(session: Session, student_identifier: str) -> dict:
        LearningProfileService.initialize_profile(
            session,
            student_identifier,
            commit=True,
        )
        student, profile, mastery, profile_data = (
            LearningProfileService._load_state(session, student_identifier)
        )
        return LearningProfileService._serialize_snapshot(
            session,
            student,
            profile,
            mastery,
            profile_data,
        )

    @staticmethod
    def get_mastery(session: Session, student_identifier: str) -> list[dict]:
        LearningProfileService.initialize_profile(
            session,
            student_identifier,
            commit=True,
        )
        _, _, mastery, _ = LearningProfileService._load_state(
            session,
            student_identifier,
        )
        return LearningProfileService._mastery_items(session, mastery)

    @staticmethod
    def apply_ai_signal(
        session: Session,
        student_identifier: str,
        ai_signal: dict[str, Any],
        *,
        commit: bool = True,
    ) -> dict:
        student, profile, mastery, profile_data = (
            LearningProfileService._load_state(session, student_identifier)
        )
        confusion = _clamp(float(ai_signal.get("confusion_level", 0.0)))
        raw_gap = ai_signal.get("knowledge_gap")
        node_id = LearningProfileService._known_node_id(session, raw_gap)
        changed_nodes: set[str] = set()

        if node_id is not None:
            mastery_delta = 0.05 + (0.10 * confusion)
            confidence_delta = 0.05 + (0.05 * confusion)
            mastery[node_id] = _clamp(
                mastery.get(node_id, MASTERY_DEFAULT) - mastery_delta
            )
            profile.confidence = _clamp(profile.confidence - confidence_delta)
            changed_nodes.add(node_id)

        preference = ai_signal.get("learning_preference")
        if preference in {"basic", "example", "fast"}:
            profile.learning_preference = preference

        suggested_action = ai_signal.get("suggested_action")
        if node_id is not None and confusion >= 0.6:
            recent_state = "confused"
        elif preference == "example" and suggested_action == "provide_example":
            recent_state = "needs_example"
        elif confusion <= 0.25:
            recent_state = "ready_to_advance"
        else:
            recent_state = "focused"

        stored_signal = dict(ai_signal)
        stored_signal["knowledge_gap"] = node_id
        stored_signal["confusion_level"] = confusion
        profile_data["last_ai_signal"] = stored_signal
        profile_data["recent_state"] = recent_state
        LearningProfileService._persist_state(
            profile,
            mastery,
            profile_data,
            changed_nodes,
        )
        LearningProfileService._finish(session, commit)
        if commit:
            logger.info(
                "Learning profile updated from AI signal student_id=%s "
                "knowledge_gap=%s confusion_level=%s confidence=%.4f",
                student.student_id,
                node_id,
                confusion,
                profile.confidence,
            )
        return LearningProfileService._serialize_snapshot(
            session,
            student,
            profile,
            mastery,
            profile_data,
        )

    @staticmethod
    def apply_learning_event(
        session: Session,
        student_identifier: str,
        node_id: str,
        result: str | None,
        *,
        commit: bool = True,
    ) -> dict:
        if result not in {"correct", "wrong", "completed", None}:
            raise ConflictError(f"Unsupported profile event result: {result}")

        student, profile, mastery, profile_data = (
            LearningProfileService._load_state(session, student_identifier)
        )
        canonical_node_id = LearningProfileService._known_node_id(session, node_id)
        if canonical_node_id is None:
            raise NotFoundError(f"Knowledge node not found: {node_id}")

        current_mastery = mastery.get(canonical_node_id, MASTERY_DEFAULT)
        changed_nodes: set[str] = set()
        if result == "correct":
            mastery[canonical_node_id] = _clamp(
                current_mastery + CORRECT_MASTERY_DELTA
            )
            profile.confidence = _clamp(
                profile.confidence + CORRECT_CONFIDENCE_DELTA
            )
            recent_state = "focused"
            changed_nodes.add(canonical_node_id)
        elif result == "wrong":
            mastery[canonical_node_id] = _clamp(
                current_mastery - WRONG_MASTERY_DELTA
            )
            profile.confidence = _clamp(
                profile.confidence - WRONG_CONFIDENCE_DELTA
            )
            recent_state = "confused"
            changed_nodes.add(canonical_node_id)
        elif result == "completed":
            recent_state = "focused"
        else:
            recent_state = profile_data.get("recent_state", "focused")

        profile.learning_speed = LearningProfileService._calculate_speed(
            session,
            student.student_id,
            profile.learning_speed,
        )
        profile_data["last_learning_event"] = {
            "node_id": canonical_node_id,
            "result": result,
        }
        profile_data["recent_state"] = recent_state
        LearningProfileService._persist_state(
            profile,
            mastery,
            profile_data,
            changed_nodes,
        )
        LearningProfileService._finish(session, commit)
        if commit:
            logger.info(
                "Learning profile updated from event student_id=%s node_id=%s "
                "result=%s confidence=%.4f mastery=%.4f",
                student.student_id,
                canonical_node_id,
                result,
                profile.confidence,
                mastery.get(canonical_node_id, MASTERY_DEFAULT),
            )
        return LearningProfileService._serialize_snapshot(
            session,
            student,
            profile,
            mastery,
            profile_data,
        )

    @staticmethod
    def record_profile_event(
        session: Session,
        student_identifier: str,
        node_id: str,
        result: str,
    ) -> dict:
        student = LearningProfileService._resolve_student(session, student_identifier)
        canonical_node_id = LearningProfileService._known_node_id(session, node_id)
        if canonical_node_id is None:
            raise NotFoundError(f"Knowledge node not found: {node_id}")

        event = LearningEvent(
            student_id=student.student_id,
            node_id=canonical_node_id,
            event_type="quiz",
            result=result,
            score=1.0 if result == "correct" else 0.0,
            time_spent=None,
        )
        try:
            session.add(event)
            session.flush()
            profile = LearningProfileService.apply_learning_event(
                session,
                student.student_id,
                canonical_node_id,
                result,
                commit=False,
            )
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise AppError("Unable to save profile event", status_code=500) from exc
        logger.info(
            "Profile event persisted student_id=%s node_id=%s result=%s",
            student.student_id,
            canonical_node_id,
            result,
        )
        return {"event_saved": True, "profile": profile}

    @staticmethod
    def _load_state(
        session: Session,
        student_identifier: str,
    ) -> tuple[Student, StudentProfile, dict[str, float], dict[str, Any]]:
        student = LearningProfileService._resolve_student(session, student_identifier)
        profile = LearningProfileService.initialize_profile(
            session,
            student.student_id,
            commit=False,
        )
        mastery = LearningProfileService._parse_mastery(profile)
        profile_data = parse_json(
            profile.profile_json,
            "student_profiles.profile_json",
        )
        if not isinstance(profile_data, dict):
            raise ConflictError("student_profiles.profile_json must be a JSON object")
        return student, profile, mastery, profile_data

    @staticmethod
    def _parse_mastery(profile: StudentProfile) -> dict[str, float]:
        raw_mastery = parse_json(
            profile.mastery_json,
            "student_profiles.mastery_json",
        )
        if not isinstance(raw_mastery, dict):
            raise ConflictError("student_profiles.mastery_json must be a JSON object")
        mastery: dict[str, float] = {}
        for node_id, value in raw_mastery.items():
            if not isinstance(node_id, str) or not isinstance(value, (int, float)):
                raise ConflictError("student_profiles.mastery_json has invalid values")
            mastery[node_id] = _clamp(float(value))
        return mastery

    @staticmethod
    def _serialize_basic_profile(
        session: Session,
        student: Student,
        profile: StudentProfile,
        profile_data: dict[str, Any],
    ) -> dict:
        goal = (
            session.get(LearningGoal, student.current_goal_id)
            if student.current_goal_id
            else None
        )
        path = PathService.get_current_model(session, student.student_id)
        weak_node_ids = profile_data.get("weak_points", [])
        weak_nodes = session.scalars(
            select(KnowledgeNode).where(KnowledgeNode.node_id.in_(weak_node_ids))
        ).all()
        names_by_id = {node.node_id: node.name for node in weak_nodes}
        return {
            "student_id": student.student_id,
            "learning_speed": profile.learning_speed,
            "learning_preference": profile.learning_preference,
            "confidence": _clamp(profile.confidence),
            "current_goal": goal.title if goal else None,
            "current_path": path.path_name,
            "weak_points": [
                names_by_id[node_id]
                for node_id in weak_node_ids
                if node_id in names_by_id
            ],
            "recent_state": profile_data.get("recent_state", "focused"),
        }

    @staticmethod
    def _serialize_snapshot(
        session: Session,
        student: Student,
        profile: StudentProfile,
        mastery: dict[str, float],
        profile_data: dict[str, Any],
    ) -> dict:
        return {
            **LearningProfileService._serialize_basic_profile(
                session,
                student,
                profile,
                profile_data,
            ),
            "student_name": student.name,
            "mastery": mastery,
            "mastery_items": LearningProfileService._mastery_items(
                session,
                mastery,
            ),
            "weak_point_ids": profile_data.get("weak_points", []),
            "updated_at": profile.updated_at,
        }

    @staticmethod
    def _mastery_items(
        session: Session,
        mastery: dict[str, float],
    ) -> list[dict]:
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

    @staticmethod
    def _persist_state(
        profile: StudentProfile,
        mastery: dict[str, float],
        profile_data: dict[str, Any],
        changed_nodes: set[str],
    ) -> None:
        weak_points = set(profile_data.get("weak_points", []))
        for node_id in changed_nodes:
            value = mastery[node_id]
            if value < 0.4:
                weak_points.add(node_id)
            elif value >= 0.6:
                weak_points.discard(node_id)

        ordered_weak_points = [
            node_id for node_id in mastery if node_id in weak_points
        ]
        profile.confidence = _clamp(profile.confidence)
        profile.mastery_json = json.dumps(mastery, ensure_ascii=False)
        profile_data["mastery"] = mastery
        profile_data["weak_points"] = ordered_weak_points
        profile.profile_json = json.dumps(profile_data, ensure_ascii=False)
        profile.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _calculate_speed(
        session: Session,
        student_id: str,
        current_speed: str,
    ) -> str:
        durations = session.scalars(
            select(LearningEvent.time_spent)
            .where(
                LearningEvent.student_id == student_id,
                LearningEvent.time_spent.is_not(None),
                LearningEvent.time_spent > 0,
            )
            .order_by(LearningEvent.created_at.desc(), LearningEvent.event_id.desc())
            .limit(10)
        ).all()
        if len(durations) < 3:
            return current_speed
        average_seconds = sum(durations) / len(durations)
        if average_seconds <= 240:
            return "fast"
        if average_seconds >= 480:
            return "slow"
        return "medium"

    @staticmethod
    def _known_node_id(session: Session, node_id: Any) -> str | None:
        if not isinstance(node_id, str) or not node_id:
            return None
        canonical_node_id = GRAPH_TO_SQLITE_NODE_IDS.get(node_id, node_id)
        return (
            canonical_node_id
            if session.get(KnowledgeNode, canonical_node_id) is not None
            else None
        )

    @staticmethod
    def _resolve_student(session: Session, identifier: str) -> Student:
        student = session.get(Student, identifier)
        if student is None:
            student = session.scalar(
                select(Student)
                .where(Student.name == identifier)
                .order_by(Student.student_id)
            )
        if student is None:
            raise NotFoundError(f"Student not found: {identifier}")
        return student

    @staticmethod
    def _finish(session: Session, commit: bool) -> None:
        if commit:
            session.commit()
        else:
            session.flush()


# Preserve the existing import name used by Milestones 3-7.
ProfileService = LearningProfileService
