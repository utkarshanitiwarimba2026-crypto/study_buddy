from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class QuizResult:
    """Stores the outcome of a single quiz attempt for a topic."""

    topic_id: str
    score: int
    total_questions: int
    timestamp: str
    percentage: float = 0.0
    result_id: str = ""

    def __post_init__(self) -> None:
        if not self.result_id:
            self.result_id = str(uuid.uuid4())
        self.percentage = round(self.score / self.total_questions * 100, 1) if self.total_questions else 0.0

    # ── Serialization ────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "topic_id": self.topic_id,
            "score": self.score,
            "total_questions": self.total_questions,
            "percentage": self.percentage,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuizResult":
        obj = cls(
            topic_id=data["topic_id"],
            score=data["score"],
            total_questions=data["total_questions"],
            timestamp=data["timestamp"],
            result_id=data.get("result_id", ""),
        )
        # Restore the stored percentage (don't recompute from potentially stale fields)
        obj.percentage = data.get("percentage", obj.percentage)
        return obj

    # ── Factory helper ───────────────────────────────────────────────────────

    @staticmethod
    def now_iso() -> str:
        """Return the current UTC time as an ISO 8601 string."""
        return datetime.now(timezone.utc).isoformat()
