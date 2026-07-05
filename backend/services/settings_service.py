from sqlalchemy.orm import Session

from backend.database.initializer import reset_database
from backend.models import SystemSetting
from backend.services.common import require_student


class SettingsService:
    @staticmethod
    def get_settings(session: Session) -> dict:
        keys = ("theme", "llm_provider", "model_name")
        return {
            key: setting.setting_value if setting else None
            for key in keys
            if (setting := session.get(SystemSetting, key)) is not None
        }

    @staticmethod
    def switch_student(session: Session, student_id: str) -> dict:
        require_student(session, student_id)
        setting = session.get(SystemSetting, "current_student_id")
        if setting is None:
            setting = SystemSetting(
                setting_key="current_student_id",
                setting_value=student_id,
            )
            session.add(setting)
        else:
            setting.setting_value = student_id
        session.commit()
        return {"current_student_id": student_id}

    @staticmethod
    def reset_demo() -> dict:
        reset_database()
        return {
            "reset": True,
            "message": "Demo 数据已重置。",
        }
