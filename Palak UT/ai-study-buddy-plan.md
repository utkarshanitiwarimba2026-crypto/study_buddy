# AI Study Buddy — Implementation Plan

## Top-Level Overview

**Goal:** Build a beginner-friendly, AI-powered Study Buddy web app using Python and Streamlit.  
**Scope:** Single-user, local-only app. No authentication, no database. All data stored in a JSON file on disk.  
**AI Backend:** Google Gemini API (`gemini-1.5-flash` model) — free tier, no credit card required.  
**Approach:** Build in 7 focused sub-tasks, each independently testable, from project setup through the final progress dashboard.

---

## Architecture Summary

```
study_buddy/
├── app.py                    ← Streamlit UI entry point (all pages/screens)
├── models/
│   ├── user.py               ← User dataclass
│   ├── topic.py              ← Topic dataclass
│   └── quiz_result.py        ← QuizResult dataclass
├── services/
│   ├── ai_service.py         ← All Gemini API calls
│   ├── quiz_service.py       ← Answer evaluation and scoring
│   └── progress_service.py   ← Topic completion and progress logic
├── storage/
│   └── data_store.py         ← JSON read/write for user persistence
├── utils/
│   └── validators.py         ← Input validation helpers
├── exceptions.py             ← All custom exception classes
├── requirements.txt          ← Python dependencies
└── .env                      ← Gemini API key (not committed to git)
```

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffolding and Setup

**Intent:** Create the folder structure, install dependencies, and wire up the API key so every later sub-task has a working foundation to build on.

**Expected Outcomes:**
- All folders and empty placeholder files exist
- `requirements.txt` lists all dependencies
- `.env` file holds the Gemini API key variable
- Running `streamlit run app.py` shows a blank app without errors

**Todo List:**
1. Create the folder structure shown in the Architecture Summary above
2. Create `requirements.txt` with these packages:
   - `streamlit`
   - `google-generativeai`
   - `python-dotenv`
3. Create `.env` with a placeholder: `GEMINI_API_KEY=your_key_here`
4. Create `exceptions.py` with all custom exception classes (see Sub-Task 2 for the list)
5. Add stub (empty) `__init__.py` files in each subfolder so Python treats them as packages
6. Create a minimal `app.py` that just displays a title: "AI Study Buddy"

**Relevant Context:**
- Google Gemini free tier signup: https://aistudio.google.com/
- `python-dotenv` loads the `.env` file so the API key is never hardcoded

**Status:** [ ] pending

---

### Sub-Task 2 — Data Models and Custom Exceptions

**Intent:** Define the three data classes and all custom exceptions that the rest of the app depends on. Getting these right early prevents rework in later sub-tasks.

**Expected Outcomes:**
- `User`, `Topic`, and `QuizResult` dataclasses are fully defined with all fields
- All 6 custom exceptions are defined in `exceptions.py`
- Models can be serialized to/from plain Python dicts (needed for JSON storage)

**Todo List:**
1. Implement `models/topic.py` — `Topic` dataclass with fields:
   - `topic_id: str` — unique ID, e.g. `"python_loops"`
   - `title: str` — human-readable name, e.g. `"For Loops"`
   - `subject: str` — parent subject
   - `is_completed: bool` — default `False`
   - `quiz_attempted: bool` — default `False`
   - `to_dict()` method and `from_dict()` class method for JSON serialization
2. Implement `models/quiz_result.py` — `QuizResult` dataclass with fields:
   - `result_id: str` — unique ID
   - `topic_id: str`
   - `score: int` — correct answers count
   - `total_questions: int`
   - `percentage: float` — computed as `score / total_questions * 100`
   - `timestamp: str` — ISO datetime string
   - `to_dict()` and `from_dict()` methods
3. Implement `models/user.py` — `User` dataclass with fields:
   - `name: str`
   - `subject: str`
   - `knowledge_level: str` — one of `"Beginner"`, `"Intermediate"`, `"Advanced"`
   - `topics: list[Topic]` — default empty list
   - `quiz_history: list[QuizResult]` — default empty list
   - `to_dict()` and `from_dict()` methods (must handle nested Topic and QuizResult objects)
4. Implement `exceptions.py` with these classes (all extend `Exception`):
   - `InvalidUserInputError` — name or subject fails validation
   - `InvalidLevelError` — knowledge level not in allowed values
   - `TopicNotFoundError` — topic ID does not exist for this user
   - `QuizNotAttemptedError` — tried to mark complete without quiz attempt
   - `AIServiceError` — Gemini API call failed or returned unusable output
   - `StorageError` — JSON file read/write failed

**Relevant Context:**
- Use Python `@dataclass` decorator for clean, simple model definitions
- `to_dict()` / `from_dict()` pattern allows straightforward JSON serialization without external libraries

**Status:** [ ] pending

---

### Sub-Task 3 — JSON Storage Layer

**Intent:** Build the persistence layer so user data (topics, quiz history, progress) survives between Streamlit sessions.

**Expected Outcomes:**
- A `data/` folder is created automatically on first save
- Each user's data is stored as `data/{username}.json`
- Loading a user who doesn't exist returns `None` (not an error)
- Corrupted JSON is caught gracefully and raises `StorageError`

**Todo List:**
1. Implement `storage/data_store.py` with these functions:
   - `user_exists(name: str) -> bool` — checks if `data/{name}.json` exists
   - `save_user(user: User) -> None` — serializes user to JSON and writes to file; raises `StorageError` on failure
   - `load_user(name: str) -> User | None` — reads JSON and deserializes to `User`; returns `None` if file not found; raises `StorageError` if JSON is malformed
2. Ensure the `data/` directory is created automatically if it does not exist
3. Add `data/` to `.gitignore` so user data is not committed to version control
4. Use `json.dumps` with `indent=2` for human-readable files (helpful for debugging)

**Relevant Context:**
- `User.to_dict()` and `User.from_dict()` from Sub-Task 2 are used here
- Wrap all file operations in try/except and raise `StorageError` with a descriptive message

**Status:** [ ] pending

---

### Sub-Task 4 — AI Service (Gemini Integration)

**Intent:** Wrap all Gemini API calls in a single service module. This isolates AI logic from the UI and makes it easy to swap the model later.

**Expected Outcomes:**
- Study plan generation returns a list of 5–8 topic title strings
- Quiz generation returns a list of question dicts, each with question text, 4 choices, and the correct answer letter
- Topic explanation returns a plain-text string in simple language
- All functions handle API errors gracefully and raise `AIServiceError`

**Todo List:**
1. Implement `services/ai_service.py` with three functions:

   **`generate_study_plan(subject: str, level: str) -> list[str]`**
   - Prompt Gemini to return a JSON array of 5–8 topic titles for the given subject and level
   - Parse the JSON response and return the list of strings
   - Example prompt pattern: *"You are a teacher. Return a JSON array of 5 to 8 topic titles for learning {subject} at {level} level. Return only the JSON array, no other text."*

   **`generate_quiz(topic: str, level: str) -> list[dict]`**
   - Prompt Gemini to return a JSON array of 4 quiz questions
   - Each question dict must have: `"question"`, `"choices"` (dict with keys A/B/C/D), `"answer"` (correct letter)
   - Example prompt pattern: *"Create a 4-question multiple-choice quiz about {topic} for a {level} learner. Return only a JSON array..."*

   **`explain_topic(topic: str, level: str) -> str`**
   - Prompt Gemini for a plain-language explanation of the topic suited to the knowledge level
   - Return the raw text response (no JSON parsing needed)

2. Load the Gemini API key from the `.env` file using `python-dotenv`
3. Configure the `gemini-1.5-flash` model
4. Wrap every API call in try/except; raise `AIServiceError` on failure
5. Add a simple retry: if the JSON parse fails on the first attempt, call the API once more before raising `AIServiceError`

**Relevant Context:**
- Install: `pip install google-generativeai python-dotenv`
- Gemini SDK: `import google.generativeai as genai`
- The prompts must explicitly say "return only JSON" to prevent Gemini from adding markdown code fences around the response
- Strip any leading/trailing whitespace and backtick fences before calling `json.loads()`

**Status:** [ ] pending

---

### Sub-Task 5 — Quiz and Progress Services

**Intent:** Implement the business logic for evaluating quiz answers and tracking topic completion and progress. These are pure Python functions with no UI or AI calls.

**Expected Outcomes:**
- Quiz answers are evaluated correctly and a score/percentage is returned
- Topics can be marked completed only if a quiz was attempted
- Progress summary returns accurate counts of completed vs total topics
- Improvement trend correctly identifies if recent scores are higher than earlier ones

**Todo List:**
1. Implement `services/quiz_service.py`:
   - `evaluate_answers(questions: list[dict], user_answers: dict) -> tuple[int, int]`
     - Compares user's selected answer letter against the correct answer for each question
     - Returns `(score, total)` tuple
   - `compute_percentage(score: int, total: int) -> float`
     - Returns `round(score / total * 100, 1)`

2. Implement `services/progress_service.py`:
   - `mark_topic_completed(user: User, topic_id: str) -> None`
     - Finds the topic by ID; raises `TopicNotFoundError` if not found
     - Raises `QuizNotAttemptedError` if `topic.quiz_attempted` is `False`
     - Sets `topic.is_completed = True`
   - `get_progress_summary(user: User) -> dict`
     - Returns `{"completed": int, "total": int, "percentage": float}`
   - `get_improvement_trend(user: User, topic_id: str) -> str`
     - Filters `quiz_history` to entries for the given `topic_id`
     - If fewer than 2 results: returns `"Not enough data yet"`
     - Compares the most recent percentage to the earliest; returns `"Improving"`, `"Declining"`, or `"Steady"`

3. Implement `utils/validators.py`:
   - `validate_name(name: str) -> None` — raises `InvalidUserInputError` if blank, over 50 chars, or contains non-letter/space characters
   - `validate_subject(subject: str) -> None` — raises `InvalidUserInputError` if blank or over 100 chars
   - `validate_level(level: str) -> None` — raises `InvalidLevelError` if not one of `["Beginner", "Intermediate", "Advanced"]`

**Relevant Context:**
- `User`, `Topic`, `QuizResult` models from Sub-Task 2
- Custom exceptions from `exceptions.py`

**Status:** [ ] pending

---

### Sub-Task 6 — Streamlit UI (All Screens)

**Intent:** Build the complete user interface in `app.py`. This is the only file the user directly interacts with — it connects all services and models together.

**Expected Outcomes:**
- App has 5 clearly separated pages/sections navigable via a sidebar
- Each page displays correctly and calls the right service functions
- Errors are shown as friendly Streamlit warning/error messages, never raw Python tracebacks
- Data is saved to JSON automatically after every state-changing action

**Todo List:**

1. **Landing / Profile Page**
   - Input fields for: Name, Subject (free text), Knowledge Level (selectbox: Beginner / Intermediate / Advanced)
   - On submit: validate inputs using `validators.py`; load existing user or create new one
   - Store the `User` object in `st.session_state` for the rest of the session
   - Show a warning if the user already exists: "Welcome back, {name}! Loading your saved progress."

2. **Study Plan Page**
   - Show existing topics as a list (if any exist)
   - "Generate Study Plan" button: calls `ai_service.generate_study_plan()`, creates `Topic` objects, saves user
   - Warn user if they already have a plan: "This will replace your existing plan."

3. **Topic Detail Page**
   - Selectbox to pick a topic from the user's plan
   - "Explain This Topic" button: calls `ai_service.explain_topic()`, displays explanation text
   - "Start Quiz" button: calls `ai_service.generate_quiz()`, stores questions in `st.session_state`
   - Show 4 MCQ questions as radio buttons (A/B/C/D)
   - "Submit Quiz" button: calls `quiz_service.evaluate_answers()`, creates `QuizResult`, saves user
   - After submission: show score (e.g. "3 / 4 — 75%") and which answers were correct/wrong
   - "Mark as Completed" button: calls `progress_service.mark_topic_completed()`; shows error if quiz not attempted

4. **Progress Dashboard Page**
   - Show total progress bar: e.g. "3 of 7 topics completed (43%)"
   - Show a table of all topics with their status (Completed / Pending)

5. **Quiz History Page**
   - Show a table of all past quiz attempts: Topic, Score, Percentage, Date
   - For each topic that has 2+ attempts, show the improvement trend label

**Relevant Context:**
- Use `st.session_state` to persist the User object and quiz questions during a session
- Use `st.sidebar` for page navigation
- Every time a write action succeeds, call `data_store.save_user(user)` immediately after
- Catch all custom exceptions and display them with `st.error()` or `st.warning()`
- Never call `st.rerun()` unless absolutely necessary — prefer conditional rendering

**Status:** [ ] pending

---

### Sub-Task 7 — Final Wiring, README, and Validation

**Intent:** Ensure all pieces are connected end-to-end, the app runs cleanly from a fresh clone, and a beginner can understand how to set it up and run it.

**Expected Outcomes:**
- App runs with `streamlit run app.py` after following the README
- All 5 pages work correctly in sequence (profile → plan → quiz → complete → progress)
- README explains setup in plain language for a total beginner
- No hardcoded API keys anywhere in the code

**Todo List:**
1. Final integration check: walk through the full user journey manually in the running app
2. Verify `.env` is in `.gitignore` and `data/` folder is also excluded
3. Write `README.md` with:
   - One-paragraph description of the app
   - Prerequisites: Python 3.10+, a Gemini API key
   - Step-by-step setup: clone → create venv → `pip install -r requirements.txt` → add API key to `.env` → `streamlit run app.py`
   - Screenshot placeholder section
   - Brief description of each page
4. Verify all imports are correct and there are no circular imports between modules
5. Confirm error messages in the UI are human-readable and never expose raw exception details to the user

**Relevant Context:**
- Get a free Gemini API key at: https://aistudio.google.com/
- The `data/` folder is auto-created by `data_store.py` — no manual step needed

**Status:** [ ] pending

---

## Business Rules Reference

| Rule | Where Enforced |
|---|---|
| User identified by name only | `data_store.py` — filename is `{name}.json` |
| Study plan tailored to knowledge level | `ai_service.generate_study_plan()` prompt |
| Quiz must have at least 3 questions | `ai_service.generate_quiz()` — prompts for 4; retries if fewer than 3 returned |
| Topic completable only after quiz attempt | `progress_service.mark_topic_completed()` |
| Quiz scores stored with timestamp | `QuizResult.timestamp` set at creation time |
| Progress = completed / total * 100 | `progress_service.get_progress_summary()` |
| Trend = compare oldest vs newest score | `progress_service.get_improvement_trend()` |
| AI called only for plan, quiz, explain | Only `ai_service.py` touches the Gemini API |
