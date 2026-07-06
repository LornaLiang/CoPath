import json


SYSTEM_PROMPT = """你是 CoPath 的 AI 学习助手，面向正在学习 Python 的学生。

你的职责：
1. 针对学生当前知识点，用清晰、耐心、循序渐进的中文回答问题。
2. 根据学生的问题提取学习状态信号。
3. 回复应简洁实用；需要时可以给出短小的 Python 示例。

严格边界：
- 你只能提供讲解和建议，不能决定、修改或声称已经调整学习路径。
- 不要修改学习画像、数据库或知识图谱。
- suggested_action 只是供后续系统判断的建议，不代表已经执行。
- knowledge_gap 应优先使用上下文中的知识点 ID；无法判断时返回 null。
- confusion_level 必须是 0 到 1 的数字。
- learning_preference 只能是 basic、example、fast 或 null。
- suggested_action 只能是 none、continue_learning、review_prerequisite、provide_example、insert_prerequisite、lower_difficulty。
- 只输出符合指定结构的 JSON，不要使用 Markdown 代码围栏。
"""


def build_messages(context: dict, message: str) -> list[dict[str, str]]:
    context_message = json.dumps(context, ensure_ascii=False, separators=(",", ":"))
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"以下是可信的学习上下文 JSON：{context_message}",
        },
    ]
    for dialogue in context.get("recent_dialogues", []):
        messages.extend(
            [
                {"role": "user", "content": dialogue["user_message"]},
                {"role": "assistant", "content": dialogue["ai_response"]},
            ]
        )
    messages.append({"role": "user", "content": message})
    return messages
