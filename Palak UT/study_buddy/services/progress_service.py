from __future__ import annotations

from study_buddy.exceptions import QuizNotAttemptedError, TopicNotFoundError
from study_buddy.models.user import User


# ── Topic completion ──────────────────────────────────────────────────────────


def mark_topic_completed(user: User, topic_id: str) -> None:
    """Mark the topic identified by *topic_id* as completed.

    Raises:
        TopicNotFoundError: if no topic with *topic_id* exists.
        QuizNotAttemptedError: if the topic's quiz has not been attempted.
    """
    topic = _find_topic(user, topic_id)
    if not topic.quiz_attempted:
        raise QuizNotAttemptedError(
            f"Please complete a quiz on '{topic.title}' before marking it as done."
        )
    topic.is_completed = True


def _find_topic(user: User, topic_id: str):  # type: ignore[return]
    """Return the topic matching *topic_id*, or raise TopicNotFoundError."""
    for topic in user.topics:
        if topic.topic_id == topic_id:
            return topic
    raise TopicNotFoundError(f"Topic '{topic_id}' not found.")


# ── Progress summary ──────────────────────────────────────────────────────────


def get_progress_summary(user: User) -> dict[str, int | float]:
    """Return a dict with completed count, total count, and percentage."""
    total = len(user.topics)
    completed = sum(1 for t in user.topics if t.is_completed)
    percentage = round(completed / total * 100, 1) if total else 0.0
    return {"completed": completed, "total": total, "percentage": percentage}


# ── Improvement trend ─────────────────────────────────────────────────────────


def get_improvement_trend(user: User, topic_id: str) -> str:
    """Describe the score trend for a given topic over multiple attempts.

    Returns one of: ``"Improving"``, ``"Declining"``, ``"Steady"``,
    or ``"Not enough data yet"`` when fewer than 2 attempts exist.
    """
    results = [r for r in user.quiz_history if r.topic_id == topic_id]
    if len(results) < 2:
        return "Not enough data yet"

    # Sort by timestamp (ISO strings sort lexicographically)
    results_sorted = sorted(results, key=lambda r: r.timestamp)
    first_pct = results_sorted[0].percentage
    last_pct = results_sorted[-1].percentage

    if last_pct > first_pct:
        return "Improving"
    if last_pct < first_pct:
        return "Declining"
    return "Steady"
