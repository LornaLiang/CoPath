from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import KnowledgeNode, Student, SystemSetting
from backend.utils.errors import NotFoundError


def require_student(session: Session, student_id: str) -> Student:
    student = session.get(Student, student_id)
    if student is None:
        raise NotFoundError(f"Student not found: {student_id}")
    return student


def require_node(session: Session, node_id: str) -> KnowledgeNode:
    node = session.get(KnowledgeNode, node_id)
    if node is None:
        raise NotFoundError(f"Knowledge node not found: {node_id}")
    return node


def get_current_student_id(session: Session) -> str:
    setting = session.get(SystemSetting, "current_student_id")
    if setting is not None:
        return setting.setting_value

    student_id = session.scalar(select(Student.student_id).order_by(Student.student_id))
    if student_id is None:
        raise NotFoundError("No demo students are available")
    return student_id


def serialize_resource(resource) -> dict:
    return {
        "resource_id": resource.resource_id,
        "title": resource.title,
        "resource_type": resource.resource_type,
        "url": resource.url or "",
        "content": resource.content or "",
        "difficulty": resource.difficulty,
    }
