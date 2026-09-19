"""Unit tests for AI Study Buddy core logic.

Run with:  pytest study_buddy/tests/ -v
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from study_buddy.exceptions import (
    InvalidLevelError,
    InvalidUserInputError,
    QuizNotAttemptedError,
    StorageError,
    TopicNotFoundError,
)
from study_buddy.models.quiz_result import QuizResult
from study_buddy.models.topic import Topic
from study_buddy.models.user import User
from study_buddy.services import ai_service, progress_service, quiz_service
from study_buddy.services.quiz_service import compute_percentage, evaluate_answers
from study_buddy.services.progress_service import (
    get_improvement_trend,
    get_progress_summary,
    mark_topic_completed,
)
from study_buddy.utils.validators import validate_level, validate_name, validate_subject


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_user(num_topics: int = 3) -> User:
    topics = [
        Topic(topic_id=f"t{i}", title=f"Topic {i}", subject="Python")
        for i in range(num_topics)
    ]
    return User(name="Alice", subject="Python", knowledge_level="Beginner", topics=topics)


def _make_quiz_result(topic_id: str, score: int, total: int, timestamp: str) -> QuizResult:
    r = QuizResult(topic_id=topic_id, score=score, total_questions=total, timestamp=timestamp)
    return r


# ══════════════════════════════════════════════════════════════════════════════
# MODEL TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestTopicSerialization:
    def test_round_trip(self) -> None:
        t = Topic(topic_id="p_loops", title="Loops", subject="Python", is_completed=True, quiz_attempted=True)
        assert Topic.from_dict(t.to_dict()) == t

    def test_defaults_are_false(self) -> None:
        t = Topic.from_dict({"topic_id": "x", "title": "X", "subject": "Math"})
        assert t.is_completed is False
        assert t.quiz_attempted is False


class TestQuizResultSerialization:
    def test_percentage_computed_on_init(self) -> None:
        r = QuizResult(topic_id="t1", score=3, total_questions=4, timestamp="2024-01-01T00:00:00+00:00")
        assert r.percentage == 75.0

    def test_round_trip(self) -> None:
        r = QuizResult(topic_id="t1", score=2, total_questions=4, timestamp="2024-01-01T00:00:00+00:00")
        restored = QuizResult.from_dict(r.to_dict())
        assert restored.topic_id == r.topic_id
        assert restored.score == r.score
        assert restored.percentage == r.percentage

    def test_zero_total_gives_zero_pct(self) -> None:
        r = QuizResult(topic_id="t1", score=0, total_questions=0, timestamp="2024-01-01T00:00:00+00:00")
        assert r.percentage == 0.0


class TestUserSerialization:
    def test_round_trip_empty(self) -> None:
        u = User(name="Bob", subject="Algebra", knowledge_level="Beginner")
        restored = User.from_dict(u.to_dict())
        assert restored.name == "Bob"
        assert restored.topics == []
        assert restored.quiz_history == []

    def test_round_trip_with_nested_objects(self) -> None:
        u = _make_user(2)
        u.topics[0].is_completed = True
        restored = User.from_dict(u.to_dict())
        assert len(restored.topics) == 2
        assert restored.topics[0].is_completed is True


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATOR TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestValidateName:
    def test_valid_name(self) -> None:
        validate_name("Alice")  # must not raise

    def test_empty_raises(self) -> None:
        with pytest.raises(InvalidUserInputError):
            validate_name("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidUserInputError):
            validate_name("   ")

    def test_too_long_raises(self) -> None:
        with pytest.raises(InvalidUserInputError):
            validate_name("A" * 51)

    def test_numbers_raises(self) -> None:
        with pytest.raises(InvalidUserInputError):
            validate_name("Alice123")

    def test_spaces_allowed(self) -> None:
        validate_name("Mary Jane")  # must not raise


class TestValidateSubject:
    def test_valid_subject(self) -> None:
        validate_subject("Python")

    def test_empty_raises(self) -> None:
        with pytest.raises(InvalidUserInputError):
            validate_subject("")

    def test_too_long_raises(self) -> None:
        with pytest.raises(InvalidUserInputError):
            validate_subject("x" * 101)


class TestValidateLevel:
    @pytest.mark.parametrize("level", ["Beginner", "Intermediate", "Advanced"])
    def test_valid_levels(self, level: str) -> None:
        validate_level(level)

    def test_invalid_level_raises(self) -> None:
        with pytest.raises(InvalidLevelError):
            validate_level("Expert")

    def test_case_sensitive(self) -> None:
        with pytest.raises(InvalidLevelError):
            validate_level("beginner")


# ══════════════════════════════════════════════════════════════════════════════
# QUIZ SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestEvaluateAnswers:
    def _questions(self) -> list[dict]:
        return [
            {"question": "Q1", "choices": {}, "answer": "A"},
            {"question": "Q2", "choices": {}, "answer": "B"},
            {"question": "Q3", "choices": {}, "answer": "C"},
        ]

    def test_all_correct(self) -> None:
        score, total = evaluate_answers(self._questions(), {0: "A", 1: "B", 2: "C"})
        assert score == 3
        assert total == 3

    def test_all_wrong(self) -> None:
        score, total = evaluate_answers(self._questions(), {0: "D", 1: "D", 2: "D"})
        assert score == 0
        assert total == 3

    def test_partial_correct(self) -> None:
        score, total = evaluate_answers(self._questions(), {0: "A", 1: "D", 2: "D"})
        assert score == 1
        assert total == 3

    def test_empty_answers_gives_zero(self) -> None:
        score, total = evaluate_answers(self._questions(), {})
        assert score == 0
        assert total == 3

    def test_case_insensitive(self) -> None:
        score, _ = evaluate_answers(self._questions(), {0: "a", 1: "b", 2: "c"})
        assert score == 3


class TestComputePercentage:
    def test_full_marks(self) -> None:
        assert compute_percentage(4, 4) == 100.0

    def test_zero_score(self) -> None:
        assert compute_percentage(0, 4) == 0.0

    def test_partial(self) -> None:
        assert compute_percentage(3, 4) == 75.0

    def test_zero_total(self) -> None:
        assert compute_percentage(0, 0) == 0.0

    def test_rounding(self) -> None:
        # 1/3 = 33.333... → rounds to 33.3
        assert compute_percentage(1, 3) == 33.3


# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestGetProgressSummary:
    def test_empty_topics(self) -> None:
        u = User(name="X", subject="Y", knowledge_level="Beginner")
        s = get_progress_summary(u)
        assert s == {"completed": 0, "total": 0, "percentage": 0.0}

    def test_none_completed(self) -> None:
        u = _make_user(4)
        s = get_progress_summary(u)
        assert s["completed"] == 0
        assert s["total"] == 4
        assert s["percentage"] == 0.0

    def test_all_completed(self) -> None:
        u = _make_user(3)
        for t in u.topics:
            t.is_completed = True
        s = get_progress_summary(u)
        assert s["completed"] == 3
        assert s["percentage"] == 100.0

    def test_partial_completion(self) -> None:
        u = _make_user(4)
        u.topics[0].is_completed = True
        u.topics[1].is_completed = True
        s = get_progress_summary(u)
        assert s["completed"] == 2
        assert s["percentage"] == 50.0


class TestMarkTopicCompleted:
    def test_success(self) -> None:
        u = _make_user(2)
        u.topics[0].quiz_attempted = True
        mark_topic_completed(u, "t0")
        assert u.topics[0].is_completed is True

    def test_topic_not_found_raises(self) -> None:
        u = _make_user(1)
        with pytest.raises(TopicNotFoundError):
            mark_topic_completed(u, "nonexistent")

    def test_quiz_not_attempted_raises(self) -> None:
        u = _make_user(1)
        with pytest.raises(QuizNotAttemptedError):
            mark_topic_completed(u, "t0")


class TestGetImprovementTrend:
    def test_not_enough_data(self) -> None:
        u = _make_user(1)
        assert get_improvement_trend(u, "t0") == "Not enough data yet"

    def test_improving(self) -> None:
        u = _make_user(1)
        u.quiz_history = [
            _make_quiz_result("t0", 1, 4, "2024-01-01T00:00:00+00:00"),
            _make_quiz_result("t0", 4, 4, "2024-06-01T00:00:00+00:00"),
        ]
        assert get_improvement_trend(u, "t0") == "Improving"

    def test_declining(self) -> None:
        u = _make_user(1)
        u.quiz_history = [
            _make_quiz_result("t0", 4, 4, "2024-01-01T00:00:00+00:00"),
            _make_quiz_result("t0", 1, 4, "2024-06-01T00:00:00+00:00"),
        ]
        assert get_improvement_trend(u, "t0") == "Declining"

    def test_steady(self) -> None:
        u = _make_user(1)
        u.quiz_history = [
            _make_quiz_result("t0", 2, 4, "2024-01-01T00:00:00+00:00"),
            _make_quiz_result("t0", 2, 4, "2024-06-01T00:00:00+00:00"),
        ]
        assert get_improvement_trend(u, "t0") == "Steady"


# ══════════════════════════════════════════════════════════════════════════════
# AI SERVICE TESTS (template-based, no network calls)
# ══════════════════════════════════════════════════════════════════════════════


class TestGenerateStudyPlan:
    def test_known_subject_beginner(self) -> None:
        plan = ai_service.generate_study_plan("Python", "Beginner")
        assert isinstance(plan, list)
        assert len(plan) >= 5
        assert all(isinstance(t, str) for t in plan)

    def test_known_subject_advanced(self) -> None:
        plan = ai_service.generate_study_plan("Python", "Advanced")
        assert len(plan) >= 5

    def test_unknown_subject_returns_generic(self) -> None:
        plan = ai_service.generate_study_plan("Quantum Basket Weaving", "Beginner")
        assert isinstance(plan, list)
        assert len(plan) >= 3

    def test_returns_new_list_each_call(self) -> None:
        plan1 = ai_service.generate_study_plan("Python", "Beginner")
        plan2 = ai_service.generate_study_plan("Python", "Beginner")
        assert plan1 == plan2  # same content
        assert plan1 is not plan2  # different list objects (defensive copy)


class TestGenerateQuiz:
    def test_known_topic_returns_questions(self) -> None:
        questions = ai_service.generate_quiz("Variables and data types", "Beginner")
        assert isinstance(questions, list)
        assert len(questions) >= 3
        for q in questions:
            assert "question" in q
            assert "choices" in q
            assert "answer" in q
            assert q["answer"] in q["choices"]

    def test_unknown_topic_returns_generic(self) -> None:
        questions = ai_service.generate_quiz("Something obscure", "Beginner")
        assert len(questions) >= 3

    def test_choices_are_abcd(self) -> None:
        questions = ai_service.generate_quiz("Variables and data types", "Beginner")
        for q in questions:
            assert set(q["choices"].keys()) == {"A", "B", "C", "D"}


class TestExplainTopic:
    def test_known_topic_returns_string(self) -> None:
        explanation = ai_service.explain_topic("Variables and data types", "Beginner")
        assert isinstance(explanation, str)
        assert len(explanation) > 20

    def test_unknown_topic_returns_generic(self) -> None:
        explanation = ai_service.explain_topic("Obscure topic xyz", "Beginner")
        assert isinstance(explanation, str)
        assert len(explanation) > 20

    def test_level_note_appended(self) -> None:
        exp = ai_service.explain_topic("Variables and data types", "Beginner")
        assert "Beginner tip" in exp


# ══════════════════════════════════════════════════════════════════════════════
# STORAGE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestDataStore:
    def test_save_and_load_round_trip(self, tmp_path: Path) -> None:
        from study_buddy.storage import data_store

        with patch.object(data_store, "_DATA_DIR", tmp_path):
            u = _make_user(2)
            data_store.save_user(u)
            loaded = data_store.load_user(u.name)
            assert loaded is not None
            assert loaded.name == u.name
            assert len(loaded.topics) == 2

    def test_user_exists_false_for_new_user(self, tmp_path: Path) -> None:
        from study_buddy.storage import data_store

        with patch.object(data_store, "_DATA_DIR", tmp_path):
            assert data_store.user_exists("nobody") is False

    def test_user_exists_true_after_save(self, tmp_path: Path) -> None:
        from study_buddy.storage import data_store

        with patch.object(data_store, "_DATA_DIR", tmp_path):
            u = _make_user(1)
            data_store.save_user(u)
            assert data_store.user_exists(u.name) is True

    def test_load_nonexistent_returns_none(self, tmp_path: Path) -> None:
        from study_buddy.storage import data_store

        with patch.object(data_store, "_DATA_DIR", tmp_path):
            assert data_store.load_user("ghost") is None

    def test_load_corrupted_file_raises_storage_error(self, tmp_path: Path) -> None:
        from study_buddy.storage import data_store

        with patch.object(data_store, "_DATA_DIR", tmp_path):
            bad_file = tmp_path / "corrupted.json"
            bad_file.write_text("{{not valid json", encoding="utf-8")
            # Manually mock _user_path to point at the bad file
            with patch.object(data_store, "_user_path", return_value=bad_file):
                with pytest.raises(StorageError):
                    data_store.load_user("corrupted")
