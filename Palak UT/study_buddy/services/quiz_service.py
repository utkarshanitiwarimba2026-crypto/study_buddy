from __future__ import annotations

from study_buddy.exceptions import QuizNotAttemptedError, TopicNotFoundError
from study_buddy.models.user import User


# ── Quiz evaluation ───────────────────────────────────────────────────────────


def evaluate_answers(
    questions: list[dict],
    user_answers: dict[int, str],
) -> tuple[int, int]:
    """Compare *user_answers* against the correct answers in *questions*.

    Args:
        questions: List of question dicts, each with an ``"answer"`` key
                   holding the correct letter (A/B/C/D).
        user_answers: Mapping of question index → selected letter.

    Returns:
        A ``(score, total)`` tuple.
    """
    total = len(questions)
    score = sum(
        1
        for idx, question in enumerate(questions)
        if user_answers.get(idx, "").upper() == question["answer"].upper()
    )
    return score, total


def compute_percentage(score: int, total: int) -> float:
    """Return the percentage score rounded to one decimal place."""
    if total == 0:
        return 0.0
    return round(score / total * 100, 1)
