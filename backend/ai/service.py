from threading import Lock
from typing import Any

from pydantic import ValidationError

from backend.ai.config import AISettings
from backend.ai.prompts import build_messages
from backend.ai.schemas import AIChatResult
from backend.utils.errors import AppError


class AIProviderError(AppError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message, status_code=status_code)


PATH_EXPLANATIONS = (
    "基础补全路径会先补函数、返回值和调用栈，适合前置知识不稳时降低递归学习阻力。",
    "案例驱动路径会用汉诺塔等例子带出递归思想，适合喜欢从具体情境理解概念的学生。",
    "快速提升路径会跳过大部分基础复习，直接进入递归、DFS 和回溯，适合基础扎实且学习速度快的学生。",
)


def _load_openai_symbols() -> tuple[Any, Any, Any, Any, Any]:
    try:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            OpenAI,
            OpenAIError,
        )
    except ModuleNotFoundError as exc:
        raise AIProviderError(
            "OpenAI package is not installed",
            status_code=503,
        ) from exc
    return APIConnectionError, APIStatusError, APITimeoutError, OpenAI, OpenAIError


class AIService:
    def __init__(self, settings: AISettings, client: Any | None = None) -> None:
        self.settings = settings
        self.client = None
        if settings.mode == "mock":
            return
        if client is not None:
            self.client = client
            return
        _, _, _, OpenAI, _ = _load_openai_symbols()
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=settings.timeout_seconds,
            max_retries=settings.max_retries,
        )

    @classmethod
    def from_env(cls) -> "AIService":
        return cls(AISettings.from_env())

    def close(self) -> None:
        if self.client is not None:
            self.client.close()

    def generate_reply(
        self,
        *,
        model: str,
        context: dict,
        message: str,
    ) -> AIChatResult:
        if self.settings.mode == "mock":
            return self._generate_mock_reply(context=context, message=message)

        (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            _OpenAI,
            OpenAIError,
        ) = _load_openai_symbols()
        response_format: dict[str, Any]
        if self.settings.response_format == "json_schema":
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "copath_learning_assistant_response",
                    "strict": True,
                    "schema": AIChatResult.model_json_schema(),
                },
            }
        else:
            response_format = {"type": "json_object"}

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=build_messages(context, message),
                response_format=response_format,
            )
        except (APIConnectionError, APITimeoutError) as exc:
            raise AIProviderError(
                "AI provider is temporarily unavailable",
                status_code=503,
            ) from exc
        except APIStatusError as exc:
            raise AIProviderError(
                f"AI provider request failed with HTTP {exc.status_code}"
            ) from exc
        except OpenAIError as exc:
            raise AIProviderError("AI provider request failed") from exc

        if not completion.choices:
            raise AIProviderError("AI provider returned no choices")
        content = completion.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError("AI provider returned an empty response")

        try:
            return AIChatResult.model_validate_json(content)
        except ValidationError as exc:
            raise AIProviderError(
                "AI provider returned invalid structured output"
            ) from exc

    def _generate_mock_reply(self, *, context: dict, message: str) -> AIChatResult:
        lowered_message = message.lower()
        current_node = context.get("current_node", {})
        current_node_id = current_node.get("id")
        profile = context.get("profile", {})
        student = context.get("student", {})
        recommended_path, recommendation_reason = self._recommend_mock_path(
            student,
            profile,
        )

        intent = "question_answering"
        knowledge_gap = current_node_id if isinstance(current_node_id, str) else None
        confusion_level = 0.35
        learning_preference = recommended_path
        suggested_action = "continue_learning"
        student_preference = None
        target_path_type = recommended_path
        candidate_path = recommended_path
        requires_confirmation = False

        if self._contains_any(
            lowered_message,
            ("学习目标", "学习路径", "路径推荐", "三条路径", "选哪条"),
        ):
            intent = "goal_path_explanation"
            knowledge_gap = None
            confusion_level = 0.2
            reply = (
                f"当前有三条候选路径：{PATH_EXPLANATIONS[0]}{PATH_EXPLANATIONS[1]}"
                f"{PATH_EXPLANATIONS[2]}结合你的画像，我建议先选择"
                f"{self._path_name(recommended_path)}，因为{recommendation_reason}。"
            )
        elif self._contains_any(
            lowered_message,
            ("例子", "案例", "举例", "example"),
        ):
            intent = "path_negotiation"
            knowledge_gap = (
                current_node_id if isinstance(current_node_id, str) else "recursion"
            )
            confusion_level = 0.55
            learning_preference = "example"
            suggested_action = "switch_path"
            student_preference = "example"
            target_path_type = "example"
            candidate_path = "example"
            requires_confirmation = True
            reply = (
                "可以，我们可以切换到案例驱动路径。"
                "这条路径会用具体例子先建立直觉，再回到递归规则和 DFS。"
                "如果你确认，我建议把目标路径调整为案例驱动路径。"
            )
        elif self._contains_any(
            lowered_message,
            ("直接学dfs", "直接学 dfs", "想直接学dfs", "想直接学 dfs", "跳过基础"),
        ):
            intent = "path_negotiation"
            knowledge_gap = None
            confusion_level = 0.18
            learning_preference = "fast"
            suggested_action = "skip_foundation"
            student_preference = "fast"
            target_path_type = "fast"
            candidate_path = "skip_foundation"
            requires_confirmation = True
            reply = (
                "你可以走快速提升路径，直接进入 DFS。"
                "从画像看你的基础掌握较好，我建议跳过函数和调用栈复习，"
                "但进入 DFS 前先用一个递归出口小题确认基础没有漏洞。"
            )
        elif self._contains_any(
            lowered_message,
            ("不想从基础开始", "已经会了", "我已经会", "不用从基础"),
        ):
            intent = "path_negotiation"
            knowledge_gap = None
            confusion_level = 0.25
            learning_preference = "fast"
            suggested_action = "diagnostic_check"
            student_preference = "fast"
            target_path_type = "fast"
            candidate_path = "skip_foundation"
            requires_confirmation = True
            reply = (
                f"我原本建议{self._path_name(recommended_path)}，因为{recommendation_reason}。"
                "如果你认为函数基础已经掌握，可以先做一个小测；"
                "若通过，就跳过基础节点并切到快速提升路径。"
            )
        elif self._contains_any(
            lowered_message,
            ("函数结束", "函数返回", "继续执行", "调用栈", "call stack", "stack"),
        ):
            intent = "path_negotiation"
            knowledge_gap = "call_stack"
            confusion_level = 0.82
            learning_preference = "basic"
            suggested_action = "insert_prerequisite"
            target_path_type = "basic"
            candidate_path = "basic"
            requires_confirmation = True
            reply = (
                "函数结束后还能继续执行，是因为调用栈会保存每次函数调用的返回位置。"
                "当当前函数返回时，程序会弹出这一层栈帧，然后回到上一层记录的位置继续运行。"
                "我建议你选择基础补全路径，因为你在调用栈和返回值部分掌握较弱，"
                "先补这两个前置点会让后面的递归更顺。"
            )
        elif self._contains_any(lowered_message, ("返回值", "return")):
            knowledge_gap = "return_value"
            confusion_level = 0.68
            learning_preference = "basic"
            suggested_action = "review_prerequisite"
            target_path_type = "basic"
            candidate_path = "basic"
            requires_confirmation = True
            reply = (
                "返回值会把函数内部计算出的结果交还给调用它的位置。"
                "可以先把函数调用看成一个会被结果替换的表达式。"
                "我建议先走基础补全路径，把返回值和调用栈连起来看。"
            )
        elif self._contains_any(lowered_message, ("递归", "recursion")):
            knowledge_gap = "recursion"
            confusion_level = 0.5
            learning_preference = recommended_path
            suggested_action = "provide_example"
            target_path_type = recommended_path
            candidate_path = recommended_path
            requires_confirmation = True
            reply = (
                "递归可以理解为函数把一个大问题拆成更小的同类问题。"
                "关键是先找到终止条件，再观察每一层调用如何等待下一层返回。"
                f"结合你的画像，我建议选择{self._path_name(recommended_path)}，"
                f"因为{recommendation_reason}。"
            )
        else:
            reply = (
                "我会先用一个小例子拆开这个问题，再标出你可能卡住的前置概念。"
                f"当前三条路径分别是：{PATH_EXPLANATIONS[0]}{PATH_EXPLANATIONS[1]}"
                f"{PATH_EXPLANATIONS[2]}我建议你选择{self._path_name(recommended_path)}，"
                f"因为{recommendation_reason}。"
            )

        return AIChatResult.model_validate(
            {
                "reply": reply,
                "signal": {
                    "knowledge_gap": knowledge_gap,
                    "confusion_level": confusion_level,
                    "learning_preference": learning_preference,
                    "suggested_action": suggested_action,
                    "intent": intent,
                    "recommended_path_type": recommended_path,
                    "student_preference": student_preference,
                    "target_path_type": target_path_type,
                    "candidate_path": candidate_path,
                    "requires_confirmation": requires_confirmation,
                },
            }
        )

    @staticmethod
    def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _path_name(path_type: str) -> str:
        return {
            "basic": "基础补全路径",
            "example": "案例驱动路径",
            "fast": "快速提升路径",
        }[path_type]

    @staticmethod
    def _recommend_mock_path(student: dict, profile: dict) -> tuple[str, str]:
        student_name = student.get("name")
        if student_name == "Tom":
            return "basic", "调用栈和返回值仍是薄弱点，需要先补齐前置知识"
        if student_name == "Alice":
            return "fast", "基础掌握度高、学习速度快，可以直接进入更高阶内容"
        if student_name == "Bob":
            return "example", "你偏好案例学习，适合用具体例子建立递归直觉"

        weak_points = set(profile.get("weak_points", []))
        preference = profile.get("learning_preference")
        speed = profile.get("learning_speed")
        confidence = float(profile.get("confidence") or 0.0)
        if {"调用栈", "返回值"} & weak_points:
            return "basic", "调用栈或返回值仍是薄弱点，需要先补齐前置知识"
        if preference == "example":
            return "example", "学习偏好显示你更适合通过案例理解概念"
        if speed == "fast" and confidence >= 0.8:
            return "fast", "基础较好且学习速度快，可以直接进入提升路径"
        return "basic", "当前画像还没有足够证据支持跳过前置知识"


_service: AIService | None = None
_service_lock = Lock()


def get_ai_service() -> AIService:
    global _service
    if _service is None:
        with _service_lock:
            if _service is None:
                _service = AIService.from_env()
    return _service


def close_ai_service() -> None:
    global _service
    with _service_lock:
        if _service is not None:
            _service.close()
            _service = None
