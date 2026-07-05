from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    REAL,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    avatar: Mapped[str | None] = mapped_column(Text)
    current_goal_id: Mapped[str | None] = mapped_column(
        Text,
        ForeignKey("learning_goals.goal_id"),
    )
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __table_args__ = (
        UniqueConstraint("student_id", name="uq_student_profiles_student_id"),
        CheckConstraint(
            "learning_speed IN ('slow', 'medium', 'fast')",
            name="ck_student_profiles_learning_speed",
        ),
        CheckConstraint(
            "learning_preference IN ('basic', 'example', 'fast')",
            name="ck_student_profiles_learning_preference",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_student_profiles_confidence",
        ),
        {"sqlite_autoincrement": True},
    )

    profile_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    student_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("students.student_id"),
        nullable=False,
    )
    learning_speed: Mapped[str] = mapped_column(Text, nullable=False)
    learning_preference: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(REAL, nullable=False)
    profile_json: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
