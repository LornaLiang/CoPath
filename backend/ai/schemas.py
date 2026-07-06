from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LearningSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    knowledge_gap: str | None
    confusion_level: float = Field(ge=0, le=1)
    learning_preference: Literal["basic", "example", "fast"] | None
    suggested_action: Literal[
        "none",
        "continue_learning",
        "review_prerequisite",
        "provide_example",
        "insert_prerequisite",
        "lower_difficulty",
    ]


class AIChatResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: str = Field(min_length=1, max_length=4000)
    signal: LearningSignal
