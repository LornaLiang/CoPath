import json
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import LearningPath, PathAdjustmentSuggestion
from backend.services.path_planner import PathPlanner
from backend.services.path_service import PathService
from backend.services.profile_service import LearningProfileService
from backend.utils.errors import AppError, ConflictError, NotFoundError


PATH_TYPE_NAMES = {
    "basic": "基础补全路径",
    "example": "案例驱动路径",
    "fast": "快速提升路径",
}


class PathCollaborationService:
    """Human-confirmed wrapper around deterministic PathPlanner decisions."""

    @staticmethod
    def suggest_adjustment(
        session: Session,
        student_identifier: str,
        goal_id: str,
        *,
        trigger_type: str,
        trigger_signal: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> dict | None:
        profile = LearningProfileService.get_profile_snapshot(
            session,
            student_identifier,
        )
        student_id = profile["student_id"]
        current_path = PathService.get_current_model(session, student_id)
        plan = PathPlanner.generate_path(session, student_id, goal_id)
        current_nodes = PathService.get_node_ids(current_path)

        changed = (
            plan["selected_path"] != current_path.path_type
            or plan["nodes"] != current_nodes
        )
        if not changed:
            return None

        suggestion = PathAdjustmentSuggestion(
            student_id=student_id,
            current_path_id=current_path.path_id,
            suggested_path_type=plan["selected_path"],
            suggested_nodes_json=json.dumps(plan["nodes"], ensure_ascii=False),
            trigger_type=trigger_type,
            trigger_signal_json=json.dumps(
                trigger_signal or plan["ai_signal"],
                ensure_ascii=False,
            ),
            reason=plan["reason"],
            risk_level=PathCollaborationService._risk_level(
                profile,
                current_path.path_type,
                plan["selected_path"],
            ),
            status="pending",
        )
        try:
            session.add(suggestion)
            if commit:
                session.commit()
            else:
                session.flush()
        except SQLAlchemyError as exc:
            if commit:
                session.rollback()
            raise AppError(
                "Unable to save path adjustment suggestion",
                status_code=500,
            ) from exc

        return PathCollaborationService._serialize_suggestion(session, suggestion)

    @staticmethod
    def confirm_adjustment(
        session: Session,
        student_id: str,
        suggestion_id: int,
    ) -> dict:
        suggestion = PathCollaborationService._get_suggestion(
            session,
            student_id,
            suggestion_id,
        )
        if suggestion.status != "pending":
            raise ConflictError(f"Suggestion is not pending: {suggestion.status}")

        student = LearningProfileService._resolve_student(session, student_id)
        if student.current_goal_id is None:
            raise ConflictError("Current learning goal is not selected")

        try:
            suggestion.status = "accepted"
            suggestion.confirmed_at = PathCollaborationService._now()
            plan = PathPlanner.update_path(
                session,
                student.student_id,
                student.current_goal_id,
                trigger_type=suggestion.trigger_type,
                commit=False,
            )
            suggestion.status = "applied"
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise AppError("Unable to confirm path adjustment", status_code=500) from exc

        return {
            "suggestion": PathCollaborationService._serialize_suggestion(
                session,
                suggestion,
            ),
            "path_adjusted": bool(plan["changed"]),
            "adjustment": plan,
        }

    @staticmethod
    def reject_adjustment(
        session: Session,
        student_id: str,
        suggestion_id: int,
    ) -> dict:
        suggestion = PathCollaborationService._get_suggestion(
            session,
            student_id,
            suggestion_id,
        )
        if suggestion.status != "pending":
            raise ConflictError(f"Suggestion is not pending: {suggestion.status}")
        suggestion.status = "rejected"
        suggestion.confirmed_at = PathCollaborationService._now()
        session.commit()
        return PathCollaborationService._serialize_suggestion(session, suggestion)

    @staticmethod
    def get_pending_adjustment(session: Session, student_id: str) -> dict | None:
        LearningProfileService._resolve_student(session, student_id)
        suggestion = session.scalar(
            select(PathAdjustmentSuggestion)
            .where(
                PathAdjustmentSuggestion.student_id == student_id,
                PathAdjustmentSuggestion.status == "pending",
            )
            .order_by(
                PathAdjustmentSuggestion.created_at.desc(),
                PathAdjustmentSuggestion.suggestion_id.desc(),
            )
            .limit(1)
        )
        if suggestion is None:
            return None
        return PathCollaborationService._serialize_suggestion(session, suggestion)

    @staticmethod
    def evaluate_switch(
        session: Session,
        student_id: str,
        new_path_id: str,
        *,
        force: bool = False,
    ) -> dict:
        profile = LearningProfileService.get_profile_snapshot(session, student_id)
        student = LearningProfileService._resolve_student(session, student_id)
        if student.current_goal_id is None:
            raise ConflictError("Current learning goal is not selected")

        current_path = PathService.get_current_model(session, profile["student_id"])
        target_path = session.get(LearningPath, new_path_id)
        if target_path is None or target_path.student_id != profile["student_id"]:
            raise NotFoundError(f"Learning path not found: {new_path_id}")

        plan = PathPlanner.generate_path(
            session,
            profile["student_id"],
            student.current_goal_id,
        )
        recommended_type = plan["selected_path"]
        requested_type = target_path.path_type
        recommended = requested_type == recommended_type
        risk_level = PathCollaborationService._risk_level(
            profile,
            current_path.path_type,
            requested_type,
        )
        reason = (
            f"系统当前建议 {PATH_TYPE_NAMES[recommended_type]}：{plan['reason']}"
        )
        alternative_action = (
            f"先按 {PATH_TYPE_NAMES[recommended_type]} 学习"
            if not recommended
            else "可以切换，风险较低"
        )

        result = {
            "recommended": recommended,
            "requested_path": PathService.serialize_current(session, target_path),
            "recommended_path_type": recommended_type,
            "recommended_path_name": PATH_TYPE_NAMES[recommended_type],
            "risk_level": risk_level if not recommended else "low",
            "reason": reason,
            "not_recommended_reason": (
                "" if recommended else f"当前画像更匹配 {PATH_TYPE_NAMES[recommended_type]}"
            ),
            "alternative_action": alternative_action,
            "requires_confirmation": not recommended,
            "switched": False,
            "switch_result": None,
            "suggestion": None,
        }
        if not force:
            return result

        try:
            switch_result = PathService.switch_path(
                session,
                profile["student_id"],
                new_path_id,
                "用户在风险提示后仍然切换路径。",
                commit=False,
            )
            suggestion = PathAdjustmentSuggestion(
                student_id=profile["student_id"],
                current_path_id=current_path.path_id,
                suggested_path_type=requested_type,
                suggested_nodes_json=target_path.nodes_json,
                trigger_type="manual",
                trigger_signal_json=json.dumps(
                    {
                        "requested_path_id": new_path_id,
                        "recommended_path_type": recommended_type,
                        "force": True,
                    },
                    ensure_ascii=False,
                ),
                reason=reason,
                risk_level=result["risk_level"],
                status="overridden",
                confirmed_at=PathCollaborationService._now(),
            )
            session.add(suggestion)
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise AppError("Unable to override path switch", status_code=500) from exc
        result["switched"] = True
        result["switch_result"] = switch_result
        result["suggestion"] = PathCollaborationService._serialize_suggestion(
            session,
            suggestion,
        )
        return result

    @staticmethod
    def _get_suggestion(
        session: Session,
        student_id: str,
        suggestion_id: int,
    ) -> PathAdjustmentSuggestion:
        suggestion = session.get(PathAdjustmentSuggestion, suggestion_id)
        if suggestion is None or suggestion.student_id != student_id:
            raise NotFoundError(f"Path adjustment suggestion not found: {suggestion_id}")
        return suggestion

    @staticmethod
    def _serialize_suggestion(
        session: Session,
        suggestion: PathAdjustmentSuggestion,
    ) -> dict:
        current_path = session.get(LearningPath, suggestion.current_path_id)
        nodes = json.loads(suggestion.suggested_nodes_json)
        return {
            "suggestion_id": suggestion.suggestion_id,
            "student_id": suggestion.student_id,
            "current_path_id": suggestion.current_path_id,
            "current_path_name": current_path.path_name if current_path else None,
            "suggested_path_type": suggestion.suggested_path_type,
            "suggested_path_name": PATH_TYPE_NAMES[suggestion.suggested_path_type],
            "suggested_nodes": nodes,
            "trigger_type": suggestion.trigger_type,
            "trigger_signal": json.loads(suggestion.trigger_signal_json),
            "reason": suggestion.reason,
            "risk_level": suggestion.risk_level,
            "status": suggestion.status,
            "created_at": suggestion.created_at,
            "confirmed_at": suggestion.confirmed_at,
        }

    @staticmethod
    def _risk_level(profile: dict, current_type: str, target_type: str) -> str:
        mastery = profile.get("mastery", {})
        average_mastery = sum(mastery.values()) / len(mastery) if mastery else 0.5
        weak_points = set(profile.get("weak_point_ids", []))
        confidence = float(profile.get("confidence") or 0.0)
        if target_type == "fast" and (
            average_mastery < 0.7 or confidence < 0.65 or weak_points
        ):
            return "high"
        if current_type == "basic" and target_type == "fast":
            return "high"
        if target_type != current_type:
            return "medium"
        return "low"

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
