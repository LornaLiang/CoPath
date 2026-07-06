from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RequestModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class StudentSwitchRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)


class GoalSelectRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    goal_id: str = Field(min_length=1, max_length=64)


class PathSwitchRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    new_path_id: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=500)


class LearningEventRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    node_id: str = Field(min_length=1, max_length=64)
    event_type: Literal["learn", "quiz", "finish", "pause"]
    result: Literal["correct", "wrong", "completed"] | None = None
    score: float | None = Field(default=None, ge=0, le=1)
    time_spent: int | None = Field(default=None, ge=0)


class LearningFeedbackRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    node_id: str = Field(min_length=1, max_length=64)
    feedback_type: Literal[
        "understood",
        "still_confused",
        "need_example",
        "lower_difficulty",
        "next_node",
    ]


class ChatRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    node_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=4000)


class ProfileAISignal(RequestModel):
    knowledge_gap: str | None = Field(default=None, max_length=64)
    confusion_level: float = Field(ge=0, le=1)
    learning_preference: Literal["basic", "example", "fast"] | None = None
    suggested_action: str | None = Field(default=None, max_length=64)


class ProfileUpdateRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    ai_signal: ProfileAISignal


class ProfileEventRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    node_id: str = Field(min_length=1, max_length=64)
    result: Literal["correct", "wrong"]


class PathPlanRequest(RequestModel):
    student_id: str = Field(min_length=1, max_length=64)
    goal_id: str = Field(min_length=1, max_length=64)
