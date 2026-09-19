"""AI Study Buddy — Streamlit Application
Run with:  streamlit run study_buddy/app.py
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any

# Ensure the repo root (parent of study_buddy/) is on sys.path so that
# "from study_buddy.x import y" works whether the app is launched via
#   streamlit run study_buddy/app.py   (cwd = repo root)  ← already works
#   streamlit run app.py               (cwd = study_buddy/) ← this fixes it
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import streamlit as st

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
from study_buddy.storage import data_store
from study_buddy.utils.validators import validate_level, validate_name, validate_subject

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="centered",
)

# ── Session-state helpers ─────────────────────────────────────────────────────


def _get_user() -> User | None:
    return st.session_state.get("user")


def _set_user(user: User) -> None:
    st.session_state["user"] = user


def _save(user: User) -> None:
    """Persist and update session state in one call."""
    try:
        data_store.save_user(user)
        _set_user(user)
    except StorageError as exc:
        st.error(f"Could not save your data: {exc}")


def _generate_plan(user: User) -> None:
    """Call ai_service, build Topic objects, save, and rerun."""
    with st.spinner("Building your personalised study plan…"):
        topic_titles = ai_service.generate_study_plan(user.subject, user.knowledge_level)
    user.topics = [
        Topic(
            topic_id=f"{user.subject.lower().replace(' ', '_')}_{i}",
            title=title,
            subject=user.subject,
        )
        for i, title in enumerate(topic_titles)
    ]
    _save(user)
    st.success(f"Study plan created with **{len(user.topics)} topics**!")
    st.rerun()


# ── Sidebar navigation ────────────────────────────────────────────────────────

PAGES = [
    "👤 Profile",
    "📋 Study Plan",
    "🧠 Topic & Quiz",
    "📊 Progress",
    "📈 Quiz History",
]

st.sidebar.title("📚 AI Study Buddy")
page = st.sidebar.radio("Navigate", PAGES)

user = _get_user()
if user and page != PAGES[0]:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Learner:** {user.name}")
    st.sidebar.markdown(f"**Subject:** {user.subject}")
    st.sidebar.markdown(f"**Level:** {user.knowledge_level}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Profile
# ══════════════════════════════════════════════════════════════════════════════

if page == PAGES[0]:
    st.title("👤 Welcome to AI Study Buddy")
    st.markdown(
        "Enter your details below to start or continue your personalised learning journey."
    )

    with st.form("profile_form"):
        name_input = st.text_input("Your name", max_chars=50)
        subject_input = st.text_input("Subject / topic you want to study", max_chars=100)
        level_input = st.selectbox(
            "Your current knowledge level",
            options=["Beginner", "Intermediate", "Advanced"],
        )
        submitted = st.form_submit_button("Start Learning →")

    if submitted:
        try:
            validate_name(name_input)
            validate_subject(subject_input)
            validate_level(level_input)
        except (InvalidUserInputError, InvalidLevelError) as exc:
            st.error(str(exc))
            st.stop()

        if data_store.user_exists(name_input):
            try:
                loaded = data_store.load_user(name_input)
            except StorageError as exc:
                st.error(str(exc))
                st.stop()
            assert loaded is not None
            _set_user(loaded)
            st.success(
                f"Welcome back, **{loaded.name}**! Your saved progress has been loaded."
            )
            # Update subject/level if they changed
            if loaded.subject != subject_input.strip() or loaded.knowledge_level != level_input:
                loaded.subject = subject_input.strip()
                loaded.knowledge_level = level_input
                _save(loaded)
                st.info(
                    "Your subject/level has been updated. "
                    "Note: any existing study plan was generated for the previous settings."
                )
        else:
            new_user = User(
                name=name_input.strip(),
                subject=subject_input.strip(),
                knowledge_level=level_input,
            )
            _save(new_user)
            st.success(
                f"Profile created for **{new_user.name}**! "
                "Head to **Study Plan** in the sidebar to get started."
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Study Plan
# ══════════════════════════════════════════════════════════════════════════════

elif page == PAGES[1]:
    st.title("📋 Study Plan")

    if not user:
        st.warning("Please create your profile on the **Profile** page first.")
        st.stop()

    if user.topics:
        st.markdown(f"### Your current plan for: **{user.subject}**")
        for i, topic in enumerate(user.topics, start=1):
            status = "✅" if topic.is_completed else ("🧪" if topic.quiz_attempted else "⬜")
            st.markdown(f"{status} **{i}. {topic.title}**")

        st.markdown("---")
        st.markdown("**Legend:** ✅ Completed &nbsp;&nbsp; 🧪 Quiz attempted &nbsp;&nbsp; ⬜ Not started")
        st.markdown("---")

        regenerate = st.button("🔄 Generate a new plan (replaces current plan)")
        if regenerate:
            st.warning(
                "⚠️ This will replace your existing plan and clear completion status. "
                "Your quiz history is kept."
            )
            if st.button("✅ Yes, replace my plan"):
                _generate_plan(user)

    else:
        st.info(
            f"You don't have a study plan yet for **{user.subject}** ({user.knowledge_level}). "
            "Click below to generate one!"
        )
        if st.button("✨ Generate Study Plan"):
            _generate_plan(user)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Topic & Quiz
# ══════════════════════════════════════════════════════════════════════════════

elif page == PAGES[2]:
    st.title("🧠 Topic & Quiz")

    if not user:
        st.warning("Please create your profile on the **Profile** page first.")
        st.stop()

    if not user.topics:
        st.warning("You don't have a study plan yet. Go to **Study Plan** to create one.")
        st.stop()

    topic_options = {t.title: t for t in user.topics}
    selected_title = st.selectbox("Choose a topic", list(topic_options.keys()))

    if not selected_title:
        st.stop()

    selected_topic = topic_options[selected_title]
    status_label = (
        "✅ Completed"
        if selected_topic.is_completed
        else ("🧪 Quiz attempted" if selected_topic.quiz_attempted else "⬜ Not started")
    )
    st.caption(f"Status: {status_label}")

    # ── Explanation ───────────────────────────────────────────────────────────

    with st.expander("📖 Explain this topic to me", expanded=False):
        explanation = ai_service.explain_topic(selected_title, user.knowledge_level)
        st.markdown(explanation)

    st.markdown("---")

    # ── Quiz ──────────────────────────────────────────────────────────────────

    st.subheader("📝 Take a Quiz")

    if st.button("Load quiz questions"):
        questions = ai_service.generate_quiz(selected_title, user.knowledge_level)
        st.session_state["quiz_questions"] = questions
        st.session_state["quiz_topic_id"] = selected_topic.topic_id
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_answers"] = {}

    questions: list[dict[str, Any]] = st.session_state.get("quiz_questions", [])
    current_topic_id: str = st.session_state.get("quiz_topic_id", "")
    quiz_submitted: bool = st.session_state.get("quiz_submitted", False)

    # Only show quiz if it's for the currently selected topic
    if questions and current_topic_id == selected_topic.topic_id:
        with st.form("quiz_form"):
            user_answers: dict[int, str] = {}
            for idx, q in enumerate(questions):
                choices = q["choices"]
                options = list(choices.keys())
                labels = [f"{k}: {v}" for k, v in choices.items()]
                choice = st.radio(
                    f"**Q{idx + 1}. {q['question']}**",
                    options=labels,
                    index=None,
                    key=f"q_{idx}",
                )
                if choice:
                    user_answers[idx] = choice[0]  # Extract the letter (A/B/C/D)

            submitted_quiz = st.form_submit_button("Submit Quiz ✔")

        if submitted_quiz:
            unanswered = [i + 1 for i in range(len(questions)) if i not in user_answers]
            if unanswered:
                st.error(
                    f"Please answer all questions before submitting. "
                    f"Unanswered: Q{', Q'.join(str(n) for n in unanswered)}"
                )
            else:
                score, total = quiz_service.evaluate_answers(questions, user_answers)
                pct = quiz_service.compute_percentage(score, total)

                # Persist result
                result = QuizResult(
                    topic_id=selected_topic.topic_id,
                    score=score,
                    total_questions=total,
                    timestamp=QuizResult.now_iso(),
                )
                user.quiz_history.append(result)
                selected_topic.quiz_attempted = True
                _save(user)

                st.session_state["quiz_submitted"] = True
                st.session_state["quiz_score"] = (score, total, pct)
                st.session_state["quiz_user_answers"] = user_answers

        # Show results if just submitted
        if st.session_state.get("quiz_submitted") and "quiz_score" in st.session_state:
            score, total, pct = st.session_state["quiz_score"]
            saved_answers = st.session_state.get("quiz_user_answers", {})

            if pct == 100:
                st.success(f"🎉 Perfect score! **{score}/{total}** ({pct}%)")
            elif pct >= 60:
                st.info(f"👍 Good effort! **{score}/{total}** ({pct}%)")
            else:
                st.warning(f"📚 Keep studying! **{score}/{total}** ({pct}%) — Try again after reviewing the material.")

            st.markdown("**Answer review:**")
            for idx, q in enumerate(questions):
                correct = q["answer"]
                user_ans = saved_answers.get(idx, "—")
                icon = "✅" if user_ans == correct else "❌"
                st.markdown(
                    f"{icon} Q{idx + 1}: You chose **{user_ans}**, correct answer: **{correct}**"
                )

    st.markdown("---")

    # ── Mark as completed ─────────────────────────────────────────────────────

    st.subheader("🏁 Mark as Completed")
    if st.button("Mark this topic as completed ✅"):
        try:
            progress_service.mark_topic_completed(user, selected_topic.topic_id)
            _save(user)
            st.success(f"**{selected_title}** marked as completed!")
            st.rerun()
        except (TopicNotFoundError, QuizNotAttemptedError) as exc:
            st.error(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Progress Dashboard
# ══════════════════════════════════════════════════════════════════════════════

elif page == PAGES[3]:
    st.title("📊 Progress Dashboard")

    if not user:
        st.warning("Please create your profile on the **Profile** page first.")
        st.stop()

    if not user.topics:
        st.info("No study plan yet. Go to **Study Plan** to create one.")
        st.stop()

    summary = progress_service.get_progress_summary(user)
    completed = summary["completed"]
    total = summary["total"]
    pct = summary["percentage"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Topics", total)
    col2.metric("Completed", completed)
    col3.metric("Progress", f"{pct}%")

    st.progress(int(pct))

    if pct == 100:
        st.balloons()
        st.success("🎉 Congratulations! You've completed every topic in your study plan!")

    st.markdown("---")
    st.subheader("Topic Status")

    rows = []
    for t in user.topics:
        trend = progress_service.get_improvement_trend(user, t.topic_id)
        rows.append(
            {
                "Topic": t.title,
                "Status": "✅ Completed" if t.is_completed else ("🧪 Quiz attempted" if t.quiz_attempted else "⬜ Not started"),
                "Quiz Trend": trend,
            }
        )
    st.table(rows)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Quiz History
# ══════════════════════════════════════════════════════════════════════════════

elif page == PAGES[4]:
    st.title("📈 Quiz History")

    if not user:
        st.warning("Please create your profile on the **Profile** page first.")
        st.stop()

    if not user.quiz_history:
        st.info("No quiz attempts yet. Go to **Topic & Quiz** and take your first quiz!")
        st.stop()

    # Build a lookup for topic title by ID
    topic_lookup = {t.topic_id: t.title for t in user.topics}

    history_rows = []
    for r in sorted(user.quiz_history, key=lambda x: x.timestamp, reverse=True):
        history_rows.append(
            {
                "Topic": topic_lookup.get(r.topic_id, r.topic_id),
                "Score": f"{r.score}/{r.total_questions}",
                "Percentage": f"{r.percentage}%",
                "Date": r.timestamp[:10],  # Show date part only
            }
        )
    st.subheader("All Quiz Attempts")
    st.table(history_rows)

    st.markdown("---")
    st.subheader("Score Trend per Topic")

    # For each topic that has attempts, show a mini chart
    topic_ids_with_history = list(
        dict.fromkeys(r.topic_id for r in user.quiz_history)  # preserve order
    )

    for tid in topic_ids_with_history:
        results = sorted(
            [r for r in user.quiz_history if r.topic_id == tid],
            key=lambda r: r.timestamp,
        )
        if len(results) < 2:
            continue  # Need at least 2 data points for a meaningful chart

        title = topic_lookup.get(tid, tid)
        trend = progress_service.get_improvement_trend(user, tid)
        trend_icon = {"Improving": "📈", "Declining": "📉", "Steady": "➡️"}.get(trend, "")

        st.markdown(f"**{title}** — {trend_icon} {trend}")
        chart_data = {
            "Attempt": list(range(1, len(results) + 1)),
            "Score (%)": [r.percentage for r in results],
        }

        import pandas as pd  # local import — only needed if pandas is available

        try:
            df = pd.DataFrame(chart_data).set_index("Attempt")
            st.line_chart(df)
        except ImportError:
            # Fallback: plain text list if pandas is not installed
            for i, r in enumerate(results, 1):
                st.markdown(f"  Attempt {i}: {r.percentage}%")
