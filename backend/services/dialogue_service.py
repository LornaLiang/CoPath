import json
import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.ai import get_ai_service
from backend.ai.config import AIConfigurationError
from backend.models import DialogueLog, SystemSetting
from backend.services.common import require_node, require_student
from backend.services.path_service import PathService
from backend.services.path_planner import PathPlanner
from backend.services.profile_service import LearningProfileService, ProfileService
from backend.utils.errors import AppError
from backend.utils.json import parse_json


logger = logging.getLogger(__name__)


class DialogueService:
    @staticmethod
    def list_dialogues(session: Session, student_id: str) -> list[dict]:
        require_student(session, student_id)
        dialogues = session.scalars(
            select(DialogueLog)
            .where(DialogueLog.student_id == student_id)
            .order_by(DialogueLog.created_at.asc(), DialogueLog.dialogue_id.asc())
        ).all()
        return [DialogueService._serialize(dialogue) for dialogue in dialogues]

    @staticmethod
    def create_chat(
        session: Session,
        student_id: str,
        node_id: str,
        message: str,
    ) -> dict:
        student = require_student(session, student_id)
        node = require_node(session, node_id)
        path = PathService.get_current_model(session, student_id)
        model_setting = session.get(SystemSetting, "model_name")
        if model_setting is None or not model_setting.setting_value.strip():
            raise AIConfigurationError("AI model is not configured")

        recent_dialogues = session.scalars(
            select(DialogueLog)
            .where(DialogueLog.student_id == student_id)
            .order_by(DialogueLog.created_at.desc(), DialogueLog.dialogue_id.desc())
            .limit(5)
        ).all()
        recent_history = [
            {
                "user_message": dialogue.user_message,
                "ai_response": dialogue.ai_response,
            }
            for dialogue in reversed(recent_dialogues)
        ]

        context = {
            "student": {"id": student.student_id, "name": student.name},
            "current_node": {
                "id": node.node_id,
                "name": node.name,
                "description": node.description,
                "difficulty": node.difficulty,
                "chapter": node.chapter,
            },
            "current_path": PathService.serialize_current(session, path),
            "profile": ProfileService.get_profile(session, student_id),
            "recent_dialogues": recent_history,
        }
        result = get_ai_service().generate_reply(
            model=model_setting.setting_value,
            context=context,
            message=message,
        )
        signal = result.signal.model_dump(mode="json")
        path_plan = None
        try:
            dialogue = DialogueLog(
                student_id=student_id,
                node_id=node_id,
                user_message=message,
                ai_response=result.reply,
                extracted_signal_json=json.dumps(signal, ensure_ascii=False),
            )
            session.add(dialogue)
            LearningProfileService.apply_ai_signal(
                session,
                student_id,
                signal,
                commit=False,
            )
            if student.current_goal_id:
                path_plan = PathPlanner.update_path(
                    session,
                    student_id,
                    student.current_goal_id,
                    trigger_type="dialogue",
                    commit=False,
                )
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise AppError("Unable to save AI dialogue", status_code=500) from exc

        logger.info(
            "AI output persisted student_id=%s node_id=%s knowledge_gap=%s "
            "confusion_level=%s profile_updated=true path_adjusted=%s",
            student_id,
            node_id,
            signal.get("knowledge_gap"),
            signal.get("confusion_level"),
            bool(path_plan and path_plan["changed"]),
        )
        if path_plan and path_plan["changed"]:
            logger.info(
                "Path changed from AI signal student_id=%s selected_path=%s "
                "adjustments=%s reason=%s",
                student_id,
                path_plan["selected_path"],
                len(path_plan["adjustments"]),
                path_plan["reason"],
            )

        return {
            "reply": result.reply,
            "signal": signal,
            "profile_updated": True,
            "path_adjusted": bool(path_plan and path_plan["changed"]),
            "adjustment": (
                path_plan if path_plan and path_plan["changed"] else None
            ),
        }

    @staticmethod
    def _serialize(dialogue: DialogueLog) -> dict:
        return {
            "dialogue_id": dialogue.dialogue_id,
            "node_id": dialogue.node_id,
            "user_message": dialogue.user_message,
            "ai_response": dialogue.ai_response,
            "extracted_signal": parse_json(
                dialogue.extracted_signal_json,
                "dialogue_logs.extracted_signal_json",
            ),
            "created_at": dialogue.created_at,
        }
