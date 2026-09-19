from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from study_buddy.models.topic import Topic
from study_buddy.models.quiz_result import QuizResult


@dataclass
class User:
    """Represents a learner and all their persisted data."""

    name: str
    subject: str
    knowledge_level: str
    topics: list[Topic] = field(default_factory=list)
    quiz_history: list[QuizResult] = field(default_factory=list)

    # ── Serialization ────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "subject": self.subject,
            "knowledge_level": self.knowledge_level,
            "topics": [t.to_dict() for t in self.topics],
            "quiz_history": [r.to_dict() for r in self.quiz_history],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        return cls(
            name=data["name"],
            subject=data["subject"],
            knowledge_level=data["knowledge_level"],
            topics=[Topic.from_dict(t) for t in data.get("topics", [])],
            quiz_history=[QuizResult.from_dict(r) for r in data.get("quiz_history", [])],
        )
