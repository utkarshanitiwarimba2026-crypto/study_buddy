"""End-to-end smoke test for all main user flows."""
import tempfile
import pathlib
from unittest.mock import patch

from study_buddy.models.user import User
from study_buddy.models.topic import Topic
from study_buddy.models.quiz_result import QuizResult
from study_buddy.services import ai_service, quiz_service, progress_service
from study_buddy.storage import data_store
from study_buddy.utils.validators import validate_name, validate_subject, validate_level

# Flow 1: Create user profile
validate_name("Alice")
validate_subject("Python")
validate_level("Beginner")
user = User(name="Alice", subject="Python", knowledge_level="Beginner")
print(f"[OK] Profile: {user.name}, {user.subject}, {user.knowledge_level}")

# Flow 2: Generate study plan
topics = ai_service.generate_study_plan("Python", "Beginner")
user.topics = [Topic(topic_id=f"py_{i}", title=t, subject="Python") for i, t in enumerate(topics)]
print(f"[OK] Study plan: {len(user.topics)} topics")

# Flow 3: Explain a topic
exp = ai_service.explain_topic("Variables and data types", "Beginner")
assert len(exp) > 50
print(f"[OK] Explanation: {len(exp)} chars")

# Flow 4: Take quiz and score
questions = ai_service.generate_quiz("Variables and data types", "Beginner")
correct_answers = {i: q["answer"] for i, q in enumerate(questions)}
score, total = quiz_service.evaluate_answers(questions, correct_answers)
pct = quiz_service.compute_percentage(score, total)
print(f"[OK] Quiz: {score}/{total} = {pct}%")

# Flow 5: Save quiz result
result = QuizResult(topic_id="py_1", score=score, total_questions=total, timestamp=QuizResult.now_iso())
user.quiz_history.append(result)
user.topics[1].quiz_attempted = True
print(f"[OK] QuizResult saved: {result.percentage}%")

# Flow 6: Mark topic completed
progress_service.mark_topic_completed(user, "py_1")
assert user.topics[1].is_completed
print("[OK] Topic marked completed")

# Flow 7: Progress summary
s = progress_service.get_progress_summary(user)
total_t = s["total"]
comp = s["completed"]
pct_p = s["percentage"]
print(f"[OK] Progress: {comp}/{total_t} = {pct_p}%")

# Flow 8: Trend with 1 result
trend = progress_service.get_improvement_trend(user, "py_1")
assert trend == "Not enough data yet"
print(f"[OK] Trend (1 result): {trend}")

# Flow 9: Trend with 2 results
result2 = QuizResult(topic_id="py_1", score=0, total_questions=total, timestamp="2025-01-01T00:00:00+00:00")
user.quiz_history.append(result2)
trend2 = progress_service.get_improvement_trend(user, "py_1")
assert trend2 in ("Improving", "Declining", "Steady")
print(f"[OK] Trend (2 results): {trend2}")

# Flow 10: JSON persistence
with tempfile.TemporaryDirectory() as tmpdir:
    tmp = pathlib.Path(tmpdir)
    with patch.object(data_store, "_DATA_DIR", tmp):
        data_store.save_user(user)
        loaded = data_store.load_user(user.name)
        assert loaded is not None
        assert loaded.name == user.name
        assert len(loaded.topics) == len(user.topics)
        assert len(loaded.quiz_history) == len(user.quiz_history)
        print(f"[OK] Persistence: {loaded.name} reloaded with {len(loaded.topics)} topics, {len(loaded.quiz_history)} quiz results")

print()
print("=== ALL 10 FLOWS PASSED ===")
