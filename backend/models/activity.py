from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class DialogueLog(Base):
    __tablename__ = "dialogue_logs"
    __table_args__ = {"sqlite_autoincrement": True}

    dialogue_id: Mapped[int] = mapped_column(
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
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    ai_response: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_signal_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class PathSwitchLog(Base):
    __tablename__ = "path_switch_logs"
    __table_args__ = (
        CheckConstraint(
            "trigger_type IN ('dialogue', 'quiz', 'time', 'manual')",
            name="ck_path_switch_logs_trigger_type",
        ),
        {"sqlite_autoincrement": True},
    )

    switch_id: Mapped[int] = mapped_column(
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
    old_path_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("learning_paths.path_id"),
        nullable=False,
    )
    new_path_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("learning_paths.path_id"),
        nullable=False,
    )
    trigger_type: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_signal_json: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
