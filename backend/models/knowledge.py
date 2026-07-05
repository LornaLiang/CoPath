from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    node_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    chapter: Mapped[str] = mapped_column(Text, nullable=False)


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "target_id",
            "relation",
            name="uq_knowledge_edges_relation",
        ),
        {"sqlite_autoincrement": True},
    )

    edge_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    source_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
        index=True,
    )
    relation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'prerequisite'"),
    )


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    goal_id: Mapped[str] = mapped_column(Text, primary_key=True)
    target_node_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_level: Mapped[str] = mapped_column(Text, nullable=False)


class LearningResource(Base):
    __tablename__ = "learning_resources"
    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('video', 'text', 'exercise', 'code')",
            name="ck_learning_resources_type",
        ),
    )

    resource_id: Mapped[str] = mapped_column(Text, primary_key=True)
    node_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
