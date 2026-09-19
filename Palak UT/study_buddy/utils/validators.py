from __future__ import annotations

import re

from study_buddy.exceptions import InvalidLevelError, InvalidUserInputError

ALLOWED_LEVELS = ("Beginner", "Intermediate", "Advanced")


def validate_name(name: str) -> None:
    """Raise InvalidUserInputError if *name* is blank, too long, or contains
    non-letter/space characters."""
    stripped = name.strip()
    if not stripped:
        raise InvalidUserInputError("Name cannot be empty.")
    if len(stripped) > 50:
        raise InvalidUserInputError("Name must be 50 characters or fewer.")
    if not re.fullmatch(r"[A-Za-z ]+", stripped):
        raise InvalidUserInputError("Name may only contain letters and spaces.")


def validate_subject(subject: str) -> None:
    """Raise InvalidUserInputError if *subject* is blank or too long."""
    stripped = subject.strip()
    if not stripped:
        raise InvalidUserInputError("Subject cannot be empty.")
    if len(stripped) > 100:
        raise InvalidUserInputError("Subject must be 100 characters or fewer.")


def validate_level(level: str) -> None:
    """Raise InvalidLevelError if *level* is not one of the allowed values."""
    if level not in ALLOWED_LEVELS:
        raise InvalidLevelError(
            f"Level must be one of: {', '.join(ALLOWED_LEVELS)}. Got: '{level}'."
        )
