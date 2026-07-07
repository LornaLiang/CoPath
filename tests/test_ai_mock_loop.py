import json
import os
import shutil
import socket
import sys
import tempfile
import traceback
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "demo.db"
SCENARIOS = [
    {
        "label": "Tom",
        "student_id": "S001",
        "node_id": "call_stack",
        "message": "为什么函数返回后还能继续执行？",
        "expected_signal": {
            "knowledge_gap": "call_stack",
            "confusion_level": 0.82,
            "learning_preference": "basic",
            "suggested_action": "insert_prerequisite",
            "intent": "path_negotiation",
            "recommended_path_type": "basic",
            "target_path_type": "basic",
            "candidate_path": "basic",
            "requires_confirmation": True,
        },
        "expected_path": "basic",
        "precondition_path_id": "P003",
        "decision": "accept",
    },
    {
        "label": "Bob",
        "student_id": "S003",
        "node_id": "recursion",
        "message": "能不能通过例子讲？",
        "expected_signal": {
            "learning_preference": "example",
            "suggested_action": "switch_path",
            "intent": "path_negotiation",
            "recommended_path_type": "example",
            "student_preference": "example",
            "target_path_type": "example",
            "candidate_path": "example",
            "requires_confirmation": True,
        },
        "expected_path": "example",
        "precondition_path_id": "P007",
        "decision": "reject",
    },
    {
        "label": "Alice",
        "student_id": "S002",
        "node_id": "recursion",
        "message": "我已经会递归基础了，想直接学DFS",
        "expected_signal": {
            "knowledge_gap": None,
            "confusion_level": 0.18,
            "learning_preference": "fast",
            "suggested_action": "skip_foundation",
            "intent": "path_negotiation",
            "recommended_path_type": "fast",
            "student_preference": "fast",
            "target_path_type": "fast",
            "candidate_path": "skip_foundation",
            "requires_confirmation": True,
        },
        "expected_path": "fast",
        "precondition_path_id": "P004",
        "decision": "pending",
    },
]


def _restore_database(backup_path: Path, had_database: bool) -> None:
    if had_database:
        shutil.copy2(backup_path, DATABASE_PATH)
    else:
        DATABASE_PATH.unlink(missing_ok=True)
    backup_path.unlink(missing_ok=True)


def _preflight_neo4j() -> None:
    from backend.graph.config import Neo4jSettings

    settings = Neo4jSettings.from_env()
    parsed_uri = urlparse(settings.uri)
    host = parsed_uri.hostname
    port = parsed_uri.port or 7687
    if host is None:
        raise RuntimeError(f"Invalid NEO4J_URI: {settings.uri}")

    try:
        with socket.create_connection((host, port), timeout=2):
            pass
    except OSError as exc:
        raise RuntimeError(
            f"Cannot connect to Neo4j at {host}:{port}. "
            "Start Neo4j and run scripts/init_neo4j.py before this test."
        ) from exc


def main() -> int:
    sys.path.insert(0, str(PROJECT_ROOT))
    os.environ["AI_MODE"] = "mock"

    try:
        _preflight_neo4j()
    except RuntimeError as exc:
        print(f"AI mock loop test blocked: {exc}")
        return 1

    backup_path = Path(tempfile.gettempdir()) / (
        f"copath_demo_db_before_ai_mock_{os.getpid()}.sqlite"
    )
    had_database = DATABASE_PATH.exists()
    if had_database:
        shutil.copy2(DATABASE_PATH, backup_path)

    session = None
    try:
        from scripts.init_db import initialize_demo_database

        initialize_demo_database()

        from backend.ai import close_ai_service
        from backend.database.connection import SessionLocal, engine
        from backend.graph import close_neo4j_store
        from backend.models import PathAdjustmentSuggestion, PathSwitchLog
        from backend.services.dialogue_service import DialogueService
        from backend.services.goal_service import GoalService
        from backend.services.path_collaboration_service import (
            PathCollaborationService,
        )
        from backend.services.path_service import PathService
        from backend.services.profile_service import ProfileService

        session = SessionLocal()
        goal_result = GoalService.select_goal(session, "S001", "G001")
        ai_recommendation = goal_result.get("ai_recommendation")
        if ai_recommendation is None:
            raise AssertionError("goal selection should include mock ai_recommendation")
        goal_signal = ai_recommendation["signal"]
        if goal_signal["intent"] != "goal_path_explanation":
            raise AssertionError("goal selection should explain candidate paths")
        if goal_signal["recommended_path_type"] != "basic":
            raise AssertionError("Tom goal recommendation should be basic")

        outputs = []
        for scenario in SCENARIOS:
            PathService.switch_path(
                session,
                scenario["student_id"],
                scenario["precondition_path_id"],
                "测试前置：切换到非推荐路径以验证协同建议。",
            )
            before_path = PathService.get_current_model(
                session,
                scenario["student_id"],
            )
            before_profile = ProfileService.get_profile_snapshot(
                session,
                scenario["student_id"],
            )
            before_mastery = before_profile["mastery"].get("call_stack")

            result = DialogueService.create_chat(
                session,
                scenario["student_id"],
                scenario["node_id"],
                scenario["message"],
            )
            after_profile = ProfileService.get_profile_snapshot(
                session,
                scenario["student_id"],
            )
            after_mastery = after_profile["mastery"].get("call_stack")

            for key, expected_value in scenario["expected_signal"].items():
                actual_value = result["signal"].get(key)
                if actual_value != expected_value:
                    raise AssertionError(
                        f"{scenario['label']} unexpected {key}: "
                        f"expected {expected_value!r}, got {actual_value!r}"
            )
            if not result["profile_updated"]:
                raise AssertionError(
                    f"{scenario['label']} profile_updated should be true"
                )
            if scenario["label"] == "Tom" and after_mastery >= before_mastery:
                raise AssertionError(
                    "Tom call_stack mastery should decrease after high-confusion signal"
                )

            if result["path_adjusted"]:
                raise AssertionError(
                    f"{scenario['label']} chat must not switch path automatically"
                )
            if result["adjustment"] is not None:
                raise AssertionError(
                    f"{scenario['label']} chat should return no applied adjustment"
                )

            suggestion = result["adjustment_suggestion"]
            if suggestion is None:
                raise AssertionError(
                    f"{scenario['label']} should create a pending suggestion"
                )
            if suggestion["status"] != "pending":
                raise AssertionError(
                    f"{scenario['label']} suggestion should be pending"
                )
            if suggestion["suggested_path_type"] != scenario["expected_path"]:
                raise AssertionError(
                    f"{scenario['label']} expected suggested path "
                    f"{scenario['expected_path']}, got "
                    f"{suggestion['suggested_path_type']}"
                )
            current_after_chat = PathService.get_current_model(
                session,
                scenario["student_id"],
            )
            if current_after_chat.path_id != before_path.path_id:
                raise AssertionError(
                    f"{scenario['label']} current path changed before confirmation"
                )

            decision_result = None
            if scenario["decision"] == "accept":
                decision_result = PathCollaborationService.confirm_adjustment(
                    session,
                    scenario["student_id"],
                    suggestion["suggestion_id"],
                )
                if not decision_result["path_adjusted"]:
                    raise AssertionError("Accepted suggestion should switch Tom path")
                applied = session.get(
                    PathAdjustmentSuggestion,
                    suggestion["suggestion_id"],
                )
                if applied.status != "applied":
                    raise AssertionError("Accepted suggestion should be applied")
            elif scenario["decision"] == "reject":
                decision_result = PathCollaborationService.reject_adjustment(
                    session,
                    scenario["student_id"],
                    suggestion["suggestion_id"],
                )
                current_after_reject = PathService.get_current_model(
                    session,
                    scenario["student_id"],
                )
                if current_after_reject.path_id != before_path.path_id:
                    raise AssertionError("Rejected suggestion should keep current path")
                if decision_result["status"] != "rejected":
                    raise AssertionError("Rejected suggestion should be rejected")

            outputs.append(
                {
                    "label": scenario["label"],
                    "message": scenario["message"],
                    "signal": result["signal"],
                    "profile": {
                        "before_call_stack_mastery": before_mastery,
                        "after_call_stack_mastery": after_mastery,
                        "recent_state": after_profile["recent_state"],
                    },
                    "path_adjusted": result["path_adjusted"],
                    "current_path_after_chat": current_after_chat.path_type,
                    "suggestion": suggestion,
                    "decision": scenario["decision"],
                    "decision_result": decision_result,
                }
            )

        tom_fast = session.get(PathAdjustmentSuggestion, outputs[0]["suggestion"]["suggestion_id"])
        if tom_fast.status != "applied":
            raise AssertionError("Tom accepted suggestion should be applied")

        switch_count = session.query(PathSwitchLog).count()
        evaluation = PathCollaborationService.evaluate_switch(session, "S001", "P003")
        if evaluation["recommended"]:
            raise AssertionError("Tom fast switch should require risk confirmation")
        if not evaluation["requires_confirmation"]:
            raise AssertionError("High-risk manual switch should require confirmation")
        override = PathCollaborationService.evaluate_switch(
            session,
            "S001",
            "P003",
            force=True,
        )
        if not override["switched"]:
            raise AssertionError("Forced switch should execute path switch")
        overridden = override["suggestion"]
        if overridden["status"] != "overridden":
            raise AssertionError("Forced switch should record overridden status")
        if session.query(PathSwitchLog).count() != switch_count + 1:
            raise AssertionError("Only real forced switch should add a switch log")

        print("AI mock loop test passed")
        print(
            "Goal ai_recommendation: "
            f"{json.dumps(ai_recommendation, ensure_ascii=False)}"
        )
        for output in outputs:
            profile = output["profile"]
            print(f"{output['label']} input: {output['message']}")
            print(
                f"{output['label']} ai_output: "
                f"{json.dumps(output['signal'], ensure_ascii=False)}"
            )
            print(
                f"{output['label']} profile_update: "
                f"call_stack mastery {profile['before_call_stack_mastery']} -> "
                f"{profile['after_call_stack_mastery']}, "
                f"recent_state={profile['recent_state']}"
            )
            print(
                f"{output['label']} path_planner: "
                f"path_adjusted={output['path_adjusted']}, "
                f"current_path_after_chat={output['current_path_after_chat']}, "
                f"suggestion={json.dumps(output['suggestion'], ensure_ascii=False)}, "
                f"decision={output['decision']}"
            )
        print(
            "Manual switch evaluation: "
            f"{json.dumps(evaluation, ensure_ascii=False)}"
        )
        print(
            "Manual override result: "
            f"{json.dumps(override, ensure_ascii=False)}"
        )
        return 0
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if session is not None:
            session.close()
        try:
            close_ai_service()
            close_neo4j_store()
            engine.dispose()
        except Exception:
            pass
        _restore_database(backup_path, had_database)


if __name__ == "__main__":
    raise SystemExit(main())
