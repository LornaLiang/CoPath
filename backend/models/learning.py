from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, REAL, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"
    __table_args__ = (
        CheckConstraint(
            "path_type IN ('basic', 'example', 'fast')",
            name="ck_learning_paths_type",
        ),
        CheckConstraint(
            "is_current IN (0, 1)",
            name="ck_learning_paths_is_current",
        ),
        CheckConstraint(
            "status IN ('planned', 'active', 'completed', 'switched')",
            name="ck_learning_paths_status",
        ),
        Index(
            "uq_learning_paths_current_student",
            "student_id",
            unique=True,
            sqlite_where=text("is_current = 1"),
        ),
    )

    path_id: Mapped[str] = mapped_column(Text, primary_key=True)
    student_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )
    goal_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("learning_goals.goal_id"),
        nullable=False,
    )
    path_type: Mapped[str] = mapped_column(Text, nullable=False)
    path_name: Mapped[str] = mapped_column(Text, nullable=False)
    nodes_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_current: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'planned'"),
    )
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class LearningEvent(Base):
    __tablename__ = "learning_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('learn', 'quiz', 'finish', 'pause')",
            name="ck_learning_events_type",
        ),
        {"sqlite_autoincrement": True},
    )

    event_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    student_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str | None] = mapped_column(Text)
    score: Mapped[float | None] = mapped_column(REAL)
    time_spent: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
