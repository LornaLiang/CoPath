import json
from collections import Counter
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import (
    DialogueLog,
    KnowledgeNode,
    LearningEvent,
    LearningGoal,
    LearningPath,
    PathSwitchLog,
    Student,
)
from backend.services.graph_service import GraphService
from backend.services.path_planning_rules import (
    PATH_TO_GRAPH_NODE_IDS,
    adjust_nodes,
    path_node_id,
    select_strategy,
    topological_reorder,
)
from backend.services.path_service import PathService
from backend.services.profile_service import LearningProfileService
from backend.utils.errors import NotFoundError
from backend.utils.json import parse_json


GRAPH_TO_SQLITE_GOAL_IDS = {"goal_recursion": "G001"}
PATH_NAMES = {
    "basic": "基础补全路径",
    "example": "案例驱动路径",
    "fast": "快速提升路径",
}
class PathPlanner:
    """Deterministic graph-driven path planning without LLM decisions."""

    @staticmethod
    def generate_path(
        session: Session,
        student_identifier: str,
        goal_id: str,
    ) -> dict:
        profile = LearningProfileService.get_profile_snapshot(
            session,
            student_identifier,
        )
        student_id = profile["student_id"]
        current_path = PathService.get_current_model(session, student_id)
        candidate_paths = GraphService.get_candidate_paths(goal_id)
        if not candidate_paths:
            raise NotFoundError(f"Candidate paths not found for goal: {goal_id}")

        ai_context = PathPlanner._get_ai_context(session, student_id)
        history = PathPlanner._get_learning_history(session, student_id)
        selected_type, strategy_reason = select_strategy(
            profile,
            current_path.path_type,
            ai_context,
        )
        candidate = next(
            (
                item
                for item in candidate_paths
                if item["path_type"] == selected_type
            ),
            None,
        )
        if candidate is None:
            raise NotFoundError(f"Path strategy not found: {selected_type}")

        nodes = [path_node_id(node_id) for node_id in candidate["nodes"]]
        target_node = path_node_id(GraphService.get_goal_target(goal_id)["id"])
        nodes, adjustments = adjust_nodes(
            nodes,
            target_node,
            profile["mastery"],
            ai_context["latest_signal"],
            history,
            GraphService,
        )
        nodes, reorder_adjustments = topological_reorder(nodes, GraphService)
        adjustments.extend(reorder_adjustments)

        adjustment_reason = ""
        if adjustments:
            adjustment_reason = "；" + "；".join(
                item["reason"] for item in adjustments
            )
        reason = f"{strategy_reason}{adjustment_reason}"
        return {
            "selected_path": selected_type,
            "nodes": nodes,
            "reason": reason,
            "adjustments": adjustments,
            "current_node": PathService.get_current_node_id(session, current_path),
            "current_path_type": current_path.path_type,
            "ai_signal": ai_context["latest_signal"],
            "learning_history": history,
        }

    @staticmethod
    def update_path(
        session: Session,
        student_identifier: str,
        goal_id: str,
        *,
        trigger_type: str = "manual",
        commit: bool = True,
    ) -> dict:
        plan = PathPlanner.generate_path(session, student_identifier, goal_id)
        student_id = LearningProfileService.get_profile_snapshot(
            session,
            student_identifier,
        )["student_id"]
        student = session.get(Student, student_id)
        if student is None:
            raise NotFoundError(f"Student not found: {student_identifier}")

        sqlite_goal_id = GRAPH_TO_SQLITE_GOAL_IDS.get(goal_id, goal_id)
        if session.get(LearningGoal, sqlite_goal_id) is None:
            if student.current_goal_id is None:
                raise NotFoundError(f"Learning goal not found: {goal_id}")
            sqlite_goal_id = student.current_goal_id

        current_path = PathService.get_current_model(session, student_id)
        target_path = session.scalar(
            select(LearningPath).where(
                LearningPath.student_id == student_id,
                LearningPath.goal_id == sqlite_goal_id,
                LearningPath.path_type == plan["selected_path"],
            )
        )
        if target_path is None:
            target_path = LearningPath(
                path_id=(
                    f"DYN_{student_id}_{sqlite_goal_id}_"
                    f"{plan['selected_path'].upper()}"
                ),
                student_id=student_id,
                goal_id=sqlite_goal_id,
                path_type=plan["selected_path"],
                path_name=PATH_NAMES[plan["selected_path"]],
                nodes_json="[]",
                is_current=0,
                status="planned",
                reason=plan["reason"],
            )
            session.add(target_path)
            session.flush()

        PathPlanner._ensure_sqlite_node_cache(session, plan["nodes"])
        old_node_ids = PathService.get_node_ids(target_path)
        path_switched = current_path.path_id != target_path.path_id
        nodes_changed = old_node_ids != plan["nodes"]
        changed = path_switched or nodes_changed

        if path_switched:
            current_path.is_current = 0
            current_path.status = "switched"
            session.flush()
            target_path.is_current = 1
        target_path.status = "active"
        target_path.nodes_json = json.dumps(plan["nodes"], ensure_ascii=False)
        target_path.reason = plan["reason"]

        if path_switched:
            session.add(
                PathSwitchLog(
                    student_id=student_id,
                    old_path_id=current_path.path_id,
                    new_path_id=target_path.path_id,
                    trigger_type=trigger_type,
                    trigger_signal_json=json.dumps(
                        {
                            "ai_signal": plan["ai_signal"],
                            "learning_history": plan["learning_history"],
                            "adjustments": plan["adjustments"],
                        },
                        ensure_ascii=False,
                    ),
                    reason=plan["reason"],
                )
            )

        if commit:
            session.commit()
        else:
            session.flush()

        active_path = target_path if changed else current_path
        return {
            **plan,
            "changed": changed,
            "path_switched": path_switched,
            "current_path": PathService.serialize_current(session, active_path),
            "current_node": PathService.get_current_node_id(session, active_path),
        }

    @staticmethod
    def get_current_plan(session: Session, student_identifier: str) -> dict:
        profile = LearningProfileService.get_profile_snapshot(
            session,
            student_identifier,
        )
        student = session.get(Student, profile["student_id"])
        if student is None or student.current_goal_id is None:
            raise NotFoundError(f"Current learning goal not found: {student_identifier}")
        plan = PathPlanner.generate_path(
            session,
            student.student_id,
            student.current_goal_id,
        )
        current_path = PathService.get_current_model(session, student.student_id)
        return {
            **plan,
            "current_path": PathService.serialize_current(session, current_path),
            "current_node": PathService.get_current_node_id(session, current_path),
        }

    @staticmethod
    def _get_ai_context(session: Session, student_id: str) -> dict:
        dialogues = session.scalars(
            select(DialogueLog)
            .where(DialogueLog.student_id == student_id)
            .order_by(DialogueLog.created_at.desc(), DialogueLog.dialogue_id.desc())
            .limit(5)
        ).all()
        signals = [
            parse_json(
                dialogue.extracted_signal_json,
                "dialogue_logs.extracted_signal_json",
            )
            for dialogue in dialogues
        ]
        signals = [signal for signal in signals if isinstance(signal, dict)]
        latest_signal = signals[0] if signals else {}
        preferences = [
            signal.get("learning_preference")
            for signal in signals
            if signal.get("learning_preference") in {"basic", "example", "fast"}
        ]
        sustained_preference = None
        if preferences:
            latest_preference = preferences[0]
            streak = 0
            for preference in preferences:
                if preference != latest_preference:
                    break
                streak += 1
            if streak >= 2:
                sustained_preference = latest_preference
        return {
            "latest_signal": latest_signal,
            "sustained_preference": sustained_preference,
        }

    @staticmethod
    def _get_learning_history(session: Session, student_id: str) -> dict:
        events = session.scalars(
            select(LearningEvent)
            .where(LearningEvent.student_id == student_id)
            .order_by(LearningEvent.created_at.desc(), LearningEvent.event_id.desc())
            .limit(50)
        ).all()
        correct = Counter(
            path_node_id(event.node_id)
            for event in events
            if event.result == "correct"
        )
        wrong = Counter(
            path_node_id(event.node_id)
            for event in events
            if event.result == "wrong"
        )
        attempts = Counter(path_node_id(event.node_id) for event in events)
        stuck_nodes = sorted(
            node_id
            for node_id, count in attempts.items()
            if wrong[node_id] >= 2 or (count >= 3 and correct[node_id] == 0)
        )
        return {
            "recent_correct": dict(correct),
            "recent_wrong": dict(wrong),
            "attempts": dict(attempts),
            "stuck_nodes": stuck_nodes,
        }

    @staticmethod
    def _ensure_sqlite_node_cache(session: Session, node_ids: list[str]) -> None:
        existing_ids = set(
            session.scalars(
                select(KnowledgeNode.node_id).where(KnowledgeNode.node_id.in_(node_ids))
            ).all()
        )
        for node_id in node_ids:
            if node_id in existing_ids:
                continue
            detail = GraphService.get_node_detail(
                PATH_TO_GRAPH_NODE_IDS.get(node_id, node_id)
            )
            session.add(
                KnowledgeNode(
                    node_id=node_id,
                    name=detail["name"],
                    description=detail["description"],
                    difficulty=detail["difficulty"],
                    chapter=detail["chapter"],
                )
            )
            existing_ids.add(node_id)
