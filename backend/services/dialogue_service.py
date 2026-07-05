from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import DialogueLog
from backend.services.common import require_node, require_student
from backend.utils.json import parse_json


class DialogueService:
    @staticmethod
    def list_dialogues(session: Session, student_id: str) -> list[dict]:
        require_student(session, student_id)
        dialogues = session.scalars(
            select(DialogueLog)
            .where(DialogueLog.student_id == student_id)
            .order_by(DialogueLog.created_at.asc(), DialogueLog.dialogue_id.asc())
        ).all()
        return [
            {
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
            for dialogue in dialogues
        ]

    @staticmethod
    def create_chat_placeholder(
        session: Session,
        student_id: str,
        node_id: str,
        message: str,
    ) -> dict:
        require_student(session, student_id)
        require_node(session, node_id)

        # TODO(Milestone 7): call the LLM and persist the real dialogue and signal.
        # TODO(Milestone 8/9): update the profile and evaluate path adaptation.
        return {
            "reply": "AI 助手尚未启用；当前接口仅提供 Milestone 3 占位响应。",
            "signal": {
                "knowledge_gap": None,
                "confusion_level": 0.0,
                "learning_preference": None,
                "suggested_action": "none",
            },
            "profile_updated": False,
            "path_adjusted": False,
            "adjustment": None,
        }
