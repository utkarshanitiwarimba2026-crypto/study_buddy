# ── Custom exceptions for AI Study Buddy ────────────────────────────────────


class InvalidUserInputError(Exception):
    """Raised when name or subject input fails validation."""


class InvalidLevelError(Exception):
    """Raised when the knowledge level is not one of the allowed values."""


class TopicNotFoundError(Exception):
    """Raised when a topic ID does not exist for this user."""


class QuizNotAttemptedError(Exception):
    """Raised when trying to mark a topic complete without a quiz attempt."""


class StorageError(Exception):
    """Raised when reading or writing the JSON persistence file fails."""
