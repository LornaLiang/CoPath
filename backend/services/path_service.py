import json
import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased

from backend.models import (
    KnowledgeNode,
    LearningEvent,
    LearningPath,
    PathSwitchLog,
)
from backend.services.common import require_student
from backend.utils.errors import ConflictError, NotFoundError
from backend.utils.json import parse_json


logger = logging.getLogger(__name__)


class PathService:
    @staticmethod
    def get_current_model(session: Session, student_id: str) -> LearningPath:
        require_student(session, student_id)
        path = session.scalar(
            select(LearningPath).where(
                LearningPath.student_id == student_id,
                LearningPath.is_current == 1,
            )
        )
        if path is None:
            raise NotFoundError(f"Current learning path not found: {student_id}")
        return path

    @staticmethod
    def get_node_ids(path: LearningPath) -> list[str]:
        node_ids = parse_json(path.nodes_json, "learning_paths.nodes_json")
        if not isinstance(node_ids, list) or not all(
            isinstance(node_id, str) for node_id in node_ids
        ):
            raise ConflictError(f"Invalid node list for path: {path.path_id}")
        return node_ids

    @staticmethod
    def get_current_node_id(session: Session, path: LearningPath) -> str:
        node_ids = PathService.get_node_ids(path)
        if not node_ids:
            raise ConflictError(f"Learning path has no nodes: {path.path_id}")

        latest_event = session.scalar(
            select(LearningEvent)
            .where(
                LearningEvent.student_id == path.student_id,
                LearningEvent.node_id.in_(node_ids),
            )
            .order_by(LearningEvent.created_at.desc(), LearningEvent.event_id.desc())
            .limit(1)
        )
        return latest_event.node_id if latest_event is not None else node_ids[0]

    @staticmethod
    def serialize_nodes(
        session: Session,
        path: LearningPath,
        include_progress: bool,
    ) -> list[dict]:
        node_ids = PathService.get_node_ids(path)
        nodes = session.scalars(
            select(KnowledgeNode).where(KnowledgeNode.node_id.in_(node_ids))
        ).all()
        nodes_by_id = {node.node_id: node for node in nodes}

        current_node_id = (
            PathService.get_current_node_id(session, path) if include_progress else None
        )
        current_index = (
            node_ids.index(current_node_id) if current_node_id in node_ids else 0
        )

        result = []
        for index, node_id in enumerate(node_ids):
            node = nodes_by_id.get(node_id)
            if node is None:
                raise ConflictError(f"Path references unknown node: {node_id}")

            if not include_progress:
                status = "pending"
            elif index < current_index:
                status = "completed"
            elif index == current_index:
                status = "learning"
            else:
                status = "pending"

            result.append(
                {
                    "node_id": node.node_id,
                    "name": node.name,
                    "status": status,
                }
            )
        return result

    @staticmethod
    def serialize_current(session: Session, path: LearningPath) -> dict:
        return {
            "path_id": path.path_id,
            "path_name": path.path_name,
            "path_type": path.path_type,
            "goal_id": path.goal_id,
            "current_node_id": PathService.get_current_node_id(session, path),
            "status": path.status,
            "reason": path.reason or "",
            "nodes": PathService.serialize_nodes(session, path, include_progress=True),
        }

    @staticmethod
    def get_current(session: Session, student_id: str) -> dict:
        return PathService.serialize_current(
            session,
            PathService.get_current_model(session, student_id),
        )

    @staticmethod
    def list_candidates(
        session: Session,
        student_id: str,
        goal_id: str,
    ) -> list[dict]:
        require_student(session, student_id)
        paths = session.scalars(
            select(LearningPath)
            .where(
                LearningPath.student_id == student_id,
                LearningPath.goal_id == goal_id,
            )
            .order_by(LearningPath.path_id)
        ).all()
        if not paths:
            raise NotFoundError(
                f"Candidate paths not found for student {student_id} and goal {goal_id}"
            )

        return [
            {
                "path_id": path.path_id,
                "path_type": path.path_type,
                "path_name": path.path_name,
                "is_current": bool(path.is_current),
                "nodes": PathService.serialize_nodes(
                    session,
                    path,
                    include_progress=bool(path.is_current),
                ),
            }
            for path in paths
        ]

    @staticmethod
    def switch_path(
        session: Session,
        student_id: str,
        new_path_id: str,
        reason: str,
        *,
        commit: bool = True,
    ) -> dict:
        current_path = PathService.get_current_model(session, student_id)
        new_path = session.get(LearningPath, new_path_id)
        if new_path is None or new_path.student_id != student_id:
            raise NotFoundError(f"Learning path not found: {new_path_id}")

        if current_path.path_id == new_path.path_id:
            return {
                "old_path_id": current_path.path_id,
                "new_path_id": new_path.path_id,
                "reason": reason,
            }

        try:
            current_path.is_current = 0
            current_path.status = "switched"
            session.flush()

            new_path.is_current = 1
            new_path.status = "active"
            session.add(
                PathSwitchLog(
                    student_id=student_id,
                    old_path_id=current_path.path_id,
                    new_path_id=new_path.path_id,
                    trigger_type="manual",
                    trigger_signal_json=json.dumps(
                        {"requested_path_id": new_path_id},
                        ensure_ascii=False,
                    ),
                    reason=reason,
                )
            )
            if commit:
                session.commit()
            else:
                session.flush()
        except IntegrityError as exc:
            session.rollback()
            raise ConflictError("Unable to switch the current learning path") from exc

        logger.info(
            "Path switched manually student_id=%s old_path_id=%s new_path_id=%s "
            "reason=%s",
            student_id,
            current_path.path_id,
            new_path.path_id,
            reason,
        )

        return {
            "old_path_id": current_path.path_id,
            "new_path_id": new_path.path_id,
            "reason": reason,
        }

    @staticmethod
    def list_switch_logs(session: Session, student_id: str) -> list[dict]:
        require_student(session, student_id)
        old_path = aliased(LearningPath)
        new_path = aliased(LearningPath)
        rows = session.execute(
            select(
                PathSwitchLog,
                old_path.path_name.label("old_path_name"),
                new_path.path_name.label("new_path_name"),
            )
            .join(old_path, old_path.path_id == PathSwitchLog.old_path_id)
            .join(new_path, new_path.path_id == PathSwitchLog.new_path_id)
            .where(PathSwitchLog.student_id == student_id)
            .order_by(PathSwitchLog.created_at.desc(), PathSwitchLog.switch_id.desc())
        ).all()
        return [
            {
                "switch_id": log.switch_id,
                "old_path_name": old_path_name,
                "new_path_name": new_path_name,
                "trigger_type": log.trigger_type,
                "reason": log.reason,
                "created_at": log.created_at,
            }
            for log, old_path_name, new_path_name in rows
        ]
