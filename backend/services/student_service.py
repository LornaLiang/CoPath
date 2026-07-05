from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Student, StudentProfile
from backend.services.common import get_current_student_id, require_student


class StudentService:
    @staticmethod
    def get_current(session: Session) -> dict:
        student = require_student(session, get_current_student_id(session))
        return {
            "student_id": student.student_id,
            "name": student.name,
            "avatar": student.avatar or "",
            "current_goal_id": student.current_goal_id,
        }

    @staticmethod
    def list_students(session: Session) -> list[dict]:
        rows = session.execute(
            select(Student, StudentProfile)
            .join(StudentProfile, StudentProfile.student_id == Student.student_id)
            .order_by(Student.student_id)
        ).all()
        return [
            {
                "student_id": student.student_id,
                "name": student.name,
                "learning_speed": profile.learning_speed,
                "learning_preference": profile.learning_preference,
            }
            for student, profile in rows
        ]
