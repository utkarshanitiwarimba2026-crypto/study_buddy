"""Template-based AI service.

Provides study plans, multiple-choice quizzes, and topic explanations
entirely from built-in templates — no external API key required.

Adding a new subject:
  1. Add an entry to _STUDY_PLANS with lists for each level.
  2. Add entries to _QUIZZES for as many topics as you like.
  3. Add entries to _EXPLANATIONS for each topic.

Any subject/topic not found falls back to generic content.
"""
from __future__ import annotations

from typing import Any

# ── Study plan templates ─────────────────────────────────────────────────────
# Structure: { subject_key: { level: [topic_title, ...] } }
# subject_key is lower-cased subject string for matching.

_STUDY_PLANS: dict[str, dict[str, list[str]]] = {
    "python": {
        "Beginner": [
            "What is Python and setting up",
            "Variables and data types",
            "Basic input and output",
            "Conditionals (if / else)",
            "Loops (for and while)",
            "Functions",
            "Lists and dictionaries",
        ],
        "Intermediate": [
            "Object-oriented programming basics",
            "File handling",
            "Error handling with try/except",
            "List comprehensions",
            "Modules and packages",
            "Working with JSON",
            "Introduction to libraries (os, math, random)",
        ],
        "Advanced": [
            "Decorators and closures",
            "Generators and iterators",
            "Context managers",
            "Concurrency (threading and asyncio)",
            "Type hints and mypy",
            "Testing with pytest",
            "Packaging and virtual environments",
        ],
    },
    "algebra": {
        "Beginner": [
            "Numbers and number types",
            "Order of operations (PEMDAS)",
            "Variables and expressions",
            "Solving simple equations",
            "Inequalities",
            "Graphing on a number line",
        ],
        "Intermediate": [
            "Linear equations and slope",
            "Systems of equations",
            "Polynomials",
            "Factoring",
            "Quadratic equations",
            "Rational expressions",
        ],
        "Advanced": [
            "Functions and their graphs",
            "Exponential and logarithmic functions",
            "Sequences and series",
            "Matrices and determinants",
            "Complex numbers",
            "Proof techniques",
        ],
    },
    "world war 2": {
        "Beginner": [
            "Causes of World War 2",
            "Key countries and leaders",
            "The Holocaust",
            "Major battles overview",
            "Life on the home front",
            "End of the war",
        ],
        "Intermediate": [
            "Rise of fascism in Europe",
            "The Pacific Theatre",
            "D-Day and the Western Front",
            "The Eastern Front and the USSR",
            "Allied strategy and conferences",
            "Post-war world order",
        ],
        "Advanced": [
            "Economic roots of the war",
            "Propaganda and media control",
            "Military technology and tactics",
            "Resistance movements",
            "War crimes and Nuremberg Trials",
            "Legacy and historiography",
        ],
    },
    "biology": {
        "Beginner": [
            "What is biology?",
            "Cell structure and function",
            "Genetics basics",
            "Evolution overview",
            "Ecosystems and food chains",
            "Human body systems",
        ],
        "Intermediate": [
            "DNA replication and protein synthesis",
            "Mitosis and meiosis",
            "Natural selection",
            "Photosynthesis and respiration",
            "Classification of living things",
            "Ecology and biodiversity",
        ],
        "Advanced": [
            "Molecular genetics and gene expression",
            "Evolutionary mechanisms",
            "Biotechnology and CRISPR",
            "Immunology",
            "Neuroscience basics",
            "Bioinformatics",
        ],
    },
    "history": {
        "Beginner": [
            "What is history and why it matters",
            "Ancient civilizations",
            "The Middle Ages",
            "The Renaissance",
            "The Age of Exploration",
            "The Industrial Revolution",
        ],
        "Intermediate": [
            "Political revolutions (American, French)",
            "Colonialism and imperialism",
            "World War 1",
            "The Cold War",
            "Decolonization",
            "The modern world",
        ],
        "Advanced": [
            "Historical methodology and sources",
            "Comparative history",
            "Economic history",
            "Social and cultural history",
            "Digital history",
            "Historiography",
        ],
    },
}

# ── Quiz templates ────────────────────────────────────────────────────────────
# Structure: { topic_title_lower: [ {question, choices, answer}, ... ] }

_QUIZZES: dict[str, list[dict[str, Any]]] = {
    # Python – Beginner
    "variables and data types": [
        {
            "question": "Which of the following is a valid Python variable name?",
            "choices": {"A": "1name", "B": "_my_var", "C": "my-var", "D": "class"},
            "answer": "B",
        },
        {
            "question": "What is the data type of `3.14` in Python?",
            "choices": {"A": "int", "B": "str", "C": "float", "D": "bool"},
            "answer": "C",
        },
        {
            "question": "Which function converts a number to a string in Python?",
            "choices": {"A": "int()", "B": "str()", "C": "float()", "D": "chr()"},
            "answer": "B",
        },
        {
            "question": "What does `type(True)` return?",
            "choices": {"A": "<class 'int'>", "B": "<class 'str'>", "C": "<class 'bool'>", "D": "<class 'float'>"},
            "answer": "C",
        },
    ],
    "basic input and output": [
        {
            "question": "Which function is used to display output in Python?",
            "choices": {"A": "input()", "B": "print()", "C": "show()", "D": "display()"},
            "answer": "B",
        },
        {
            "question": "What does `input()` always return?",
            "choices": {"A": "int", "B": "float", "C": "str", "D": "bool"},
            "answer": "C",
        },
        {
            "question": "How do you print 'Hello' and 'World' on the same line with a space?",
            "choices": {
                "A": 'print("Hello", "World")',
                "B": 'print("Hello") print("World")',
                "C": 'print("Hello"+"World")',
                "D": 'echo "Hello World"',
            },
            "answer": "A",
        },
    ],
    "conditionals (if / else)": [
        {
            "question": "Which keyword starts a conditional block in Python?",
            "choices": {"A": "when", "B": "if", "C": "check", "D": "case"},
            "answer": "B",
        },
        {
            "question": "What does the `elif` keyword mean?",
            "choices": {
                "A": "else if",
                "B": "end if",
                "C": "elif is not valid Python",
                "D": "evaluate if",
            },
            "answer": "A",
        },
        {
            "question": "What is the output of: `x = 5; print('big') if x > 3 else print('small')`?",
            "choices": {"A": "small", "B": "big", "C": "5", "D": "Error"},
            "answer": "B",
        },
        {
            "question": "Which comparison operator checks equality in Python?",
            "choices": {"A": "=", "B": "!=", "C": "==", "D": ":="},
            "answer": "C",
        },
    ],
    "loops (for and while)": [
        {
            "question": "What does `range(3)` produce?",
            "choices": {
                "A": "[1, 2, 3]",
                "B": "[0, 1, 2]",
                "C": "[0, 1, 2, 3]",
                "D": "[3]",
            },
            "answer": "B",
        },
        {
            "question": "Which keyword stops a loop immediately?",
            "choices": {"A": "stop", "B": "exit", "C": "break", "D": "end"},
            "answer": "C",
        },
        {
            "question": "How many times does this loop run? `for i in range(2, 6):`",
            "choices": {"A": "2", "B": "3", "C": "4", "D": "6"},
            "answer": "C",
        },
    ],
    "functions": [
        {
            "question": "Which keyword defines a function in Python?",
            "choices": {"A": "func", "B": "function", "C": "define", "D": "def"},
            "answer": "D",
        },
        {
            "question": "What does the `return` statement do?",
            "choices": {
                "A": "Prints a value",
                "B": "Sends a value back to the caller",
                "C": "Ends the program",
                "D": "Creates a variable",
            },
            "answer": "B",
        },
        {
            "question": "What is a function parameter?",
            "choices": {
                "A": "The output of a function",
                "B": "A variable inside the function body",
                "C": "An input value passed to the function",
                "D": "The function name",
            },
            "answer": "C",
        },
    ],
    "lists and dictionaries": [
        {
            "question": "How do you access the first item of a list `my_list`?",
            "choices": {
                "A": "my_list[1]",
                "B": "my_list.first()",
                "C": "my_list[0]",
                "D": "my_list[-1]",
            },
            "answer": "C",
        },
        {
            "question": "Which method adds an item to the end of a list?",
            "choices": {"A": ".add()", "B": ".insert()", "C": ".push()", "D": ".append()"},
            "answer": "D",
        },
        {
            "question": "How do you access the value for key 'age' in dict `person`?",
            "choices": {
                "A": "person.age",
                "B": 'person["age"]',
                "C": "person->age",
                "D": "person.get_key('age')",
            },
            "answer": "B",
        },
        {
            "question": "What data structure uses key-value pairs?",
            "choices": {"A": "list", "B": "tuple", "C": "set", "D": "dictionary"},
            "answer": "D",
        },
    ],
    # Algebra
    "order of operations (pemdas)": [
        {
            "question": "In PEMDAS, what does the 'P' stand for?",
            "choices": {"A": "Plus", "B": "Parentheses", "C": "Power", "D": "Product"},
            "answer": "B",
        },
        {
            "question": "What is 2 + 3 × 4?",
            "choices": {"A": "20", "B": "14", "C": "24", "D": "10"},
            "answer": "B",
        },
        {
            "question": "What is (2 + 3) × 4?",
            "choices": {"A": "14", "B": "20", "C": "10", "D": "24"},
            "answer": "B",
        },
    ],
    "solving simple equations": [
        {
            "question": "If x + 5 = 12, what is x?",
            "choices": {"A": "5", "B": "7", "C": "17", "D": "6"},
            "answer": "B",
        },
        {
            "question": "If 3x = 15, what is x?",
            "choices": {"A": "3", "B": "12", "C": "5", "D": "45"},
            "answer": "C",
        },
        {
            "question": "What operation undoes multiplication when solving an equation?",
            "choices": {"A": "addition", "B": "multiplication", "C": "division", "D": "subtraction"},
            "answer": "C",
        },
    ],
    # World War 2
    "causes of world war 2": [
        {
            "question": "Which treaty ended World War 1 and imposed harsh terms on Germany?",
            "choices": {
                "A": "Treaty of Paris",
                "B": "Treaty of Versailles",
                "C": "Treaty of Utrecht",
                "D": "Treaty of Ghent",
            },
            "answer": "B",
        },
        {
            "question": "Who was the leader of Nazi Germany?",
            "choices": {"A": "Mussolini", "B": "Stalin", "C": "Hitler", "D": "Franco"},
            "answer": "C",
        },
        {
            "question": "When did World War 2 officially begin?",
            "choices": {"A": "1935", "B": "1938", "C": "1939", "D": "1941"},
            "answer": "C",
        },
        {
            "question": "Which country did Germany invade first to start the war?",
            "choices": {"A": "France", "B": "Poland", "C": "Czechoslovakia", "D": "Austria"},
            "answer": "B",
        },
    ],
    # Cell biology
    "cell structure and function": [
        {
            "question": "What is the control center of the cell?",
            "choices": {"A": "Mitochondria", "B": "Ribosome", "C": "Nucleus", "D": "Cell wall"},
            "answer": "C",
        },
        {
            "question": "Which organelle produces energy for the cell?",
            "choices": {"A": "Nucleus", "B": "Lysosome", "C": "Vacuole", "D": "Mitochondria"},
            "answer": "D",
        },
        {
            "question": "What separates the inside of the cell from its environment?",
            "choices": {
                "A": "Nucleus",
                "B": "Cell membrane",
                "C": "Endoplasmic reticulum",
                "D": "Cytoplasm",
            },
            "answer": "B",
        },
        {
            "question": "Which type of cell has no nucleus?",
            "choices": {"A": "Animal cell", "B": "Plant cell", "C": "Prokaryotic cell", "D": "Eukaryotic cell"},
            "answer": "C",
        },
    ],
}

# ── Topic explanations ────────────────────────────────────────────────────────
# Structure: { topic_title_lower: explanation_string }

_EXPLANATIONS: dict[str, str] = {
    "variables and data types": (
        "**Variables** are like labelled boxes where you store information in your program.\n\n"
        "For example, `age = 25` creates a box called `age` and puts the number 25 inside it.\n\n"
        "**Data types** describe *what kind* of thing is stored:\n"
        "- `int` — whole numbers, like `42`\n"
        "- `float` — decimal numbers, like `3.14`\n"
        "- `str` — text, like `'hello'`\n"
        "- `bool` — True or False\n\n"
        "Python figures out the type automatically, so you don't need to declare it."
    ),
    "basic input and output": (
        "**Output** means showing information to the user. You do this with `print()`.\n\n"
        "```python\nprint('Hello, world!')\n```\n\n"
        "**Input** means asking the user to type something. You do this with `input()`.\n\n"
        "```python\nname = input('What is your name? ')\nprint('Hello,', name)\n```\n\n"
        "`input()` always returns a **string**, so if you want a number you need to convert it: `int(input('Your age: '))`."
    ),
    "conditionals (if / else)": (
        "Conditionals let your program make **decisions**.\n\n"
        "```python\nage = 18\nif age >= 18:\n    print('Adult')\nelse:\n    print('Minor')\n```\n\n"
        "- `if` checks a condition. If it's True, the indented block runs.\n"
        "- `else` runs when the condition is False.\n"
        "- `elif` lets you check extra conditions in between.\n\n"
        "The condition must be a **boolean expression** (something that is True or False)."
    ),
    "loops (for and while)": (
        "Loops let you **repeat** code without rewriting it.\n\n"
        "**For loop** — repeat a fixed number of times:\n"
        "```python\nfor i in range(5):\n    print(i)  # prints 0 1 2 3 4\n```\n\n"
        "**While loop** — repeat as long as a condition is True:\n"
        "```python\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1\n```\n\n"
        "Use `break` to exit a loop early, and `continue` to skip the current iteration."
    ),
    "functions": (
        "A **function** is a reusable block of code that does one job.\n\n"
        "```python\ndef greet(name):\n    return 'Hello, ' + name\n\nprint(greet('Alice'))  # Hello, Alice\n```\n\n"
        "- `def` starts the function definition.\n"
        "- **Parameters** are inputs (like `name` above).\n"
        "- `return` sends a result back.\n\n"
        "Functions help keep code organised and prevent you from repeating yourself."
    ),
    "lists and dictionaries": (
        "**Lists** store an ordered collection of items:\n"
        "```python\nfruits = ['apple', 'banana', 'cherry']\nprint(fruits[0])  # apple\n```\n\n"
        "**Dictionaries** store key-value pairs:\n"
        "```python\nperson = {'name': 'Alice', 'age': 25}\nprint(person['name'])  # Alice\n```\n\n"
        "Use lists when order matters; use dictionaries when you want to look things up by name."
    ),
    "order of operations (pemdas)": (
        "PEMDAS tells you the **order** in which to solve a math expression:\n\n"
        "1. **P**arentheses — solve what's inside `()` first\n"
        "2. **E**xponents — powers like `2³`\n"
        "3. **M**ultiplication and **D**ivision — left to right\n"
        "4. **A**ddition and **S**ubtraction — left to right\n\n"
        "Example: `2 + 3 × 4` → do `3 × 4 = 12` first, then `2 + 12 = 14`."
    ),
    "solving simple equations": (
        "An **equation** says two things are equal, like `x + 5 = 12`.\n\n"
        "To solve it, **isolate x** by doing the same operation to both sides:\n\n"
        "`x + 5 = 12`\n"
        "`x + 5 − 5 = 12 − 5`\n"
        "`x = 7`\n\n"
        "The golden rule: **whatever you do to one side, you must do to the other side.**"
    ),
    "causes of world war 2": (
        "World War 2 didn't start with one event — it built up over many years.\n\n"
        "**Key causes:**\n"
        "- The **Treaty of Versailles** (1919) punished Germany heavily after WW1, causing economic suffering and resentment.\n"
        "- **Adolf Hitler** and the Nazi Party rose to power promising to restore German greatness.\n"
        "- **Appeasement** — Britain and France allowed Hitler to expand without challenge, hoping to avoid war.\n"
        "- Germany invaded **Poland on 1 September 1939**, and Britain and France declared war two days later.\n\n"
        "The war is often seen as a direct consequence of the unresolved tensions left over from World War 1."
    ),
    "cell structure and function": (
        "Every living thing is made of **cells** — the smallest unit of life.\n\n"
        "**Key parts of a cell:**\n"
        "- **Nucleus** — the control center; contains DNA\n"
        "- **Cell membrane** — a thin layer that controls what enters and exits\n"
        "- **Mitochondria** — the powerhouse; makes energy (ATP)\n"
        "- **Ribosome** — makes proteins\n"
        "- **Cytoplasm** — the jelly-like fluid that fills the cell\n\n"
        "**Animal cells** have no cell wall; **Plant cells** do, plus a chloroplast for photosynthesis."
    ),
}

# ── Generic fallbacks ─────────────────────────────────────────────────────────

_GENERIC_PLAN: dict[str, list[str]] = {
    "Beginner": [
        "Introduction and overview",
        "Core concepts and vocabulary",
        "Guided practice — part 1",
        "Guided practice — part 2",
        "Review and self-assessment",
    ],
    "Intermediate": [
        "Quick recap of the basics",
        "Deeper concepts",
        "Problem-solving techniques",
        "Case studies or worked examples",
        "Practice exercises",
        "Review",
    ],
    "Advanced": [
        "Critical analysis of core theories",
        "Edge cases and nuances",
        "Advanced problem solving",
        "Cross-topic connections",
        "Real-world applications",
        "Synthesis and reflection",
    ],
}

_GENERIC_QUIZ: list[dict[str, Any]] = [
    {
        "question": "Which of the following best describes this topic?",
        "choices": {
            "A": "A method for solving problems",
            "B": "A framework for understanding concepts",
            "C": "A set of rules and principles",
            "D": "All of the above",
        },
        "answer": "D",
    },
    {
        "question": "What is the first step when approaching an unfamiliar topic?",
        "choices": {
            "A": "Jump straight to advanced material",
            "B": "Memorise all the facts immediately",
            "C": "Understand the big picture before the details",
            "D": "Skip to the exercises",
        },
        "answer": "C",
    },
    {
        "question": "Which learning strategy is most effective for long-term retention?",
        "choices": {
            "A": "Cramming the night before",
            "B": "Reading once and moving on",
            "C": "Spaced repetition and active recall",
            "D": "Watching videos passively",
        },
        "answer": "C",
    },
]

_GENERIC_EXPLANATION = (
    "This topic is an important part of your subject. "
    "Start by reading a reliable introduction, then try to explain the concept in your own words. "
    "Look for real-world examples that connect the idea to everyday life. "
    "Practice with exercises, and don't hesitate to revisit the basics if something is unclear. "
    "Consistent, focused study sessions work better than long cramming sessions."
)


# ── Public API ────────────────────────────────────────────────────────────────


def generate_study_plan(subject: str, level: str) -> list[str]:
    """Return an ordered list of topic titles for *subject* at *level*."""
    key = subject.strip().lower()
    plan = _STUDY_PLANS.get(key, {})
    return list(plan.get(level, _GENERIC_PLAN.get(level, _GENERIC_PLAN["Beginner"])))


def generate_quiz(topic: str, level: str) -> list[dict[str, Any]]:  # noqa: ARG001
    """Return a list of MCQ question dicts for *topic*.

    Each dict has keys: ``question``, ``choices`` (A/B/C/D), ``answer``.
    """
    key = topic.strip().lower()
    return list(_QUIZZES.get(key, _GENERIC_QUIZ))


def explain_topic(topic: str, level: str) -> str:
    """Return a plain-language explanation of *topic* suited to *level*."""
    key = topic.strip().lower()
    base = _EXPLANATIONS.get(key, _GENERIC_EXPLANATION)

    level_note = {
        "Beginner": "\n\n> 💡 **Beginner tip:** Don't rush. Master the basics before moving on.",
        "Intermediate": "\n\n> 💡 **Intermediate tip:** Try to connect this topic to what you already know.",
        "Advanced": "\n\n> 💡 **Advanced tip:** Look for edge cases, exceptions, and deeper theory.",
    }.get(level, "")

    return base + level_note
