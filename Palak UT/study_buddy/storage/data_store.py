from __future__ import annotations

import json
from pathlib import Path

from study_buddy.exceptions import StorageError
from study_buddy.models.user import User

# All user JSON files are stored in study_buddy/data/
_DATA_DIR = Path(__file__).parent.parent / "data"


def _user_path(name: str) -> Path:
    """Return the Path for a user's JSON file."""
    safe_name = name.strip().lower().replace(" ", "_")
    return _DATA_DIR / f"{safe_name}.json"


def user_exists(name: str) -> bool:
    """Return True if a JSON file exists for *name*."""
    return _user_path(name).exists()


def save_user(user: User) -> None:
    """Serialize *user* and write to their JSON file.

    Raises:
        StorageError: if the file cannot be written.
    """
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = _user_path(user.name)
    try:
        path.write_text(json.dumps(user.to_dict(), indent=2), encoding="utf-8")
    except OSError as exc:
        raise StorageError(f"Could not save user data: {exc}") from exc


def load_user(name: str) -> User | None:
    """Load and return a User from their JSON file, or None if not found.

    Raises:
        StorageError: if the file exists but cannot be parsed.
    """
    path = _user_path(name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return User.from_dict(data)
    except (json.JSONDecodeError, KeyError) as exc:
        raise StorageError(
            f"User file for '{name}' is corrupted and could not be loaded: {exc}"
        ) from exc
