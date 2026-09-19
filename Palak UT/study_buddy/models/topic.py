from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Topic:
    """Represents a single study topic/lesson inside a subject."""

    topic_id: str
    title: str
    subject: str
    is_completed: bool = False
    quiz_attempted: bool = False

    # ── Serialization ────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "subject": self.subject,
            "is_completed": self.is_completed,
            "quiz_attempted": self.quiz_attempted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Topic":
        return cls(
            topic_id=data["topic_id"],
            title=data["title"],
            subject=data["subject"],
            is_completed=data.get("is_completed", False),
            quiz_attempted=data.get("quiz_attempted", False),
        )
