
import json
import os
from datetime import datetime

import streamlit as st
from google import genai

# ---------------- APP CONFIG ----------------
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "studymate_data.json"
LOGO_URL = "https://treehousehighschool.com/wp-content/uploads/2025/12/imgi_4_1024.png"
MODEL_NAME = "gemini-3.8-flash"


# ---------------- LOCAL DATA ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            data.setdefault("summaries", [])
            data.setdefault("quiz_results", [])
            return data
        except (json.JSONDecodeError, OSError):
            pass

    return {"summaries": [], "quiz_results": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


# ---------------- SESSION STATE ----------------
defaults = {
    "chat_history": [],
    "quiz": None,
    "quiz_result": None,
    "page": "🏠 Dashboard",
    "latest_summary": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

data = load_data()


# ---------------- DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: #14532d;
    color: #FFD700;
    font-family: "Segoe UI", Arial, sans-serif;
}

[data-testid="stHeader"] {
    background: #14532d;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 2px solid #d5e5d8;
}

[data-testid="stSidebar"] * {
    color: #111111;
}

h1, h2, h3, h4 {
    color: #FFD700 !important;
}

p, label, li {
    color: #FFD700;
}

.sidebar-brand {
    text-align: center;
    padding: 12px 8px 18px;
}

.sidebar-logo {
    width: 112px;
    max-width: 100%;
    height: auto;
    object-fit: contain;
    background: #ffffff;
    padding: 8px;
    border: 1px solid #e2e8e3;
    border-radius: 18px;
}

.sidebar-brand h2 {
    color: #14532d !important;
    font-size: 23px;
    font-weight: 800;
    margin: 12px 0 4px;
}

.sidebar-brand p {
    color: #647067 !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
}

.hero {
    text-align: center;
    padding: 32px 24px;
    background: #ffffff;
    border: 1px solid #d5e5d8;
    border-top: 4px solid #FFD700;
    border-radius: 20px;
    margin-bottom: 26px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.hero-logo {
    width: 100px;
    height: 100px;
    object-fit: contain;
    margin-bottom: 14px;
}

.eyebrow {
    color: #176b35 !important;
    font-weight: 800;
    letter-spacing: 2px;
    font-size: 11px;
}

.hero h1 {
    color: #14532d !important;
    font-size: 42px;
    font-weight: 800;
    margin: 8px 0;
}

.hero h2 {
    color: #9a7600 !important;
    font-size: 21px;
    font-weight: 700;
}

.hero p {
    color: #414b43 !important;
    font-size: 15px;
    line-height: 1.7;
    max-width: 700px;
    margin: 0 auto;
}

.feature,
.metric-card {
    background: #ffffff;
    border: 1px solid #d5e5d8;
    border-radius: 16px;
    padding: 24px;
    min-height: 140px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
}

.feature h3,
.feature p,
.metric-card * {
    color: #111111 !important;
}

.metric-label {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #111111;
}

.metric-value {
    color: #111111;
    font-size: 32px;
    font-weight: 750;
    margin-top: 12px;
}

.st-key-study_chat_card,
.st-key-summarizer_card,
.st-key-quiz_studio_card {
    background-color: #ffffff !important;
    border: 2px solid #d5e5d8 !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.10) !important;
}

.st-key-study_chat_card h1,
.st-key-study_chat_card h2,
.st-key-study_chat_card h3,
.st-key-study_chat_card p,
.st-key-study_chat_card li,
.st-key-study_chat_card label,
.st-key-summarizer_card h1,
.st-key-summarizer_card h2,
.st-key-summarizer_card h3,
.st-key-summarizer_card p,
.st-key-summarizer_card li,
.st-key-summarizer_card label,
.st-key-quiz_studio_card h1,
.st-key-quiz_studio_card h2,
.st-key-quiz_studio_card h3,
.st-key-quiz_studio_card p,
.st-key-quiz_studio_card li,
.st-key-quiz_studio_card label {
    color: #FFD700 !important;
}

.founder {
    background: #ffffff;
    border: 1px solid #d5e5d8;
    border-radius: 16px;
    padding: 24px 12px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
}

.founder h3,
.founder p {
    color: #111111 !important;
}

/* Buttons: black text as requested */
.stButton > button,
.stFormSubmitButton > button {
    background: #FFD700 !important;
    color: #111111 !important;
    border: 1px solid #FFD700 !important;
    border-radius: 9px;
    padding: 9px 18px;
    font-weight: 700;
}

.stButton > button p,
.stFormSubmitButton > button p {
    color: #111111 !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #e6c200 !important;
    border-color: #e6c200 !important;
    color: #111111 !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: #ffffff;
    color: #111111;
    border-color: #c5d8c9;
    border-radius: 9px;
}

[data-testid="stChatInput"] textarea {
    background: #ffffff;
    color: #111111;
}

[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
    color: #FFD700;
}

[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #d5e5d8;
    border-radius: 12px;
}

[data-testid="stExpander"] * {
    color: #111111;
}

.footer {
    text-align: center;
    padding: 20px;
    color: #FFD700;
    font-size: 12px;
}

hr {
    border-color: #72977c;
}

@media (max-width: 640px) {
    .hero {
        padding: 25px 16px;
    }

    .hero-logo {
        width: 85px;
        height: 85px;
    }

    .hero h1 {
        font-size: 31px;
    }

    .hero h2 {
        font-size: 18px;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------------- GEMINI AI ----------------
def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if not api_key or not str(api_key).strip():
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Open Streamlit app settings, "
            "go to Secrets, and check that your Gemini API key is configured."
        )

    return genai.Client(api_key=api_key)


def ask_ai(prompt, system_prompt=None):
    if system_prompt is None:
        system_prompt = (
            "You are StudyMate AI, a helpful tutor for Class 10 CBSE students. "
            "Explain concepts clearly, use accurate information and examples, "
            "show working for maths, and admit uncertainty when needed."
        )

    client = get_gemini_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"system_instruction": system_prompt},
    )

    answer = response.text

    if not answer or not answer.strip():
        raise RuntimeError(
            "Gemini returned an empty response. Please try again."
        )

    return answer.strip()


# ---------------- QUIZ GENERATION ----------------
def create_quiz(topic, difficulty, count):
    prompt = f"""
Create exactly {count} multiple-choice questions about "{topic}"
for a Class 10 CBSE student. Difficulty: {difficulty}.

Return ONLY valid JSON without Markdown fences, in this format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "Brief explanation"
    }}
  ]
}}

The answer is the zero-based index of the correct option.
Use exactly four options and one correct answer per question.
Check your answers carefully.
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "system_instruction": (
                "You create accurate educational quizzes. "
                "Output valid JSON only."
            ),
            "response_mime_type": "application/json",
        },
    )

    content = response.text

    if not content:
        raise RuntimeError("Gemini returned an empty quiz. Please try again.")

    quiz = json.loads(content)
    questions = quiz.get("questions")

    if not isinstance(questions, list) or not questions:
        raise ValueError("The generated quiz format was unexpected.")

    questions = questions[:count]

    for question in questions:
        options = question.get("options")
        answer = question.get("answer")

        if (
            not isinstance(question.get("question"), str)
            or not isinstance(options, list)
            or len(options) != 4
            or not isinstance(answer, int)
            or isinstance(answer, bool)
            or answer not in range(4)
        ):
            raise ValueError("A generated quiz question has an invalid format.")

    return {"topic": topic, "questions": questions}


# ---------------- NAVIGATION ----------------
def go_to_page(page_name):
    st.session_state.page = page_name


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <img class="sidebar-logo"
                 src="{LOGO_URL}"
                 alt="Tree House High School logo">
            <h2>StudyMate AI</h2>
            <p>YOUR PERSONAL LEARNING SPACE</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    page_options = [
        "🏠 Dashboard",
        "💬 Study Chat",
        "📝 Summarizer",
        "🧠 Quiz Studio",
        "📚 My Library",
        "📊 My Progress",
    ]

    page = st.radio("YOUR WORKSPACE", page_options, key="page")

    st.divider()
    st.caption("✦ Powered by Gemini AI")


# ---------------- MAIN HEADER ----------------
st.markdown(
    f"""
    <div class="hero">
        <img class="hero-logo" src="{LOGO_URL}"
             alt="Tree House High School logo">
        <div class="eyebrow">✦ YOUR AI STUDY COMPANION</div>
        <h1>StudyMate AI</h1>
        <h2>Study smarter. Achieve more.</h2>
        <p>
            Understand concepts, organise your notes, practise quizzes,
            and keep track of your learning — all in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------- DASHBOARD ----------------
if page == "🏠 Dashboard":
    st.subheader("Welcome to your study space 👋")
    st.write("What would you like to work on today?")

    total_quizzes = len(data["quiz_results"])
    saved_notes = len(data["summaries"])
    average = (
        sum(r["percentage"] for r in data["quiz_results"]) / total_quizzes
        if total_quizzes else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'QUIZZES COMPLETED</div><div class="metric-value">'
            f'{total_quizzes}</div></div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'SAVED SUMMARIES</div><div class="metric-value">'
            f'{saved_notes}</div></div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'AVERAGE QUIZ SCORE</div><div class="metric-value">'
            f'{average:.0f}%</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### ✨ Your study tools")
    a, b, c = st.columns(3)

    with a:
        with st.container(border=True, key="study_chat_card"):
            st.markdown("### 💬")
            st.markdown("**Study Chat**")
            st.write("Understand difficult concepts with your AI tutor.")
            st.button(
                "Open Study Chat",
                use_container_width=True,
                on_click=go_to_page,
                args=("💬 Study Chat",),
            )

    with b:
        with st.container(border=True, key="summarizer_card"):
            st.markdown("### 📝")
            st.markdown("**Smart Summarizer**")
            st.write("Turn long notes into organised revision points.")
            st.button(
                "Open Summarizer",
                use_container_width=True,
                on_click=go_to_page,
                args=("📝 Summarizer",),
            )

    with c:
        with st.container(border=True, key="quiz_studio_card"):
            st.markdown("### 🧠")
            st.markdown("**Quiz Studio**")
            st.write("Generate questions and check your score.")
            st.button(
                "Open Quiz Studio",
                use_container_width=True,
                on_click=go_to_page,
                args=("🧠 Quiz Studio",),
            )

    st.markdown("### 🌱 Study tip")
    st.info(
        "Study one topic, make a short summary, and test your understanding "
        "with a quiz."
    )


# ---------------- STUDY CHAT ----------------
elif page == "💬 Study Chat":
    st.subheader("💬 Study Chat")
    st.write("Ask questions and learn at your own pace.")

    # Chat window styling
    st.markdown("""
    <style>
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #d5e5d8;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 10px;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: #111111 !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff;
        border: 2px solid #FFD700;
        border-radius: 14px;
    }

    [data-testid="stChatInput"] textarea {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Welcome message
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="
            background: #ffffff;
            border: 1px solid #d5e5d8;
            border-radius: 16px;
            padding: 22px;
            margin: 16px 0;
            text-align: center;
        ">
            <div style="font-size: 38px;">🎓</div>
            <h3 style="color: #14532d;">Hey there, learner!</h3>
            <p style="color: #414b43;">
                I'm your StudyMate AI tutor. Ask me anything about
                your Class 10 CBSE subjects, and we'll work through it together.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Display previous messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Question input box
    question = st.chat_input(
        "Ask a question about Maths, Science, English..."
    )

    if question:
        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Your AI tutor is thinking..."):
                try:
                    history_text = "\n".join(
                        f'{m["role"]}: {m["content"]}'
                        for m in st.session_state.chat_history[-11:]
                    )

                    answer = ask_ai(
                        history_text,
                        system_prompt=(
                            "You are StudyMate AI, a friendly and accurate "
                            "Class 10 CBSE tutor. Answer the student's latest "
                            "question clearly, step by step when useful. "
                            "Use simple explanations and examples. "
                            "If a question is ambiguous, ask for clarification."
                        ),
                    )

                    st.markdown(answer)

                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer}
                    )

                except Exception as error:
                    st.error(
                        f"Study Chat error: {type(error).__name__}: {error}"
                    )
                    st.info(
                        "Check your Gemini API key, model access, and API "
                        "usage limits in Google AI Studio."
                    )

    # Clear conversation
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_study_chat"):
            st.session_state.chat_history = []
            st.rerun()
```


# ---------------- SUMMARIZER ----------------
elif page == "📝 Summarizer":
    st.subheader("📝 Smart Summarizer")
    st.write("Turn your study material into clear revision notes.")

    notes = st.text_area(
        "Paste your notes",
        height=220,
        placeholder="Paste your textbook notes here...",
    )

    style = st.selectbox(
        "Summary style",
        [
            "Key points",
            "Short revision notes",
            "Important definitions",
            "Exam-focused summary",
        ],
    )

    if st.button("✨ Summarize notes", use_container_width=True):
        if not notes.strip():
            st.warning("Paste your notes first.")
        else:
            with st.spinner("Organising your notes..."):
                try:
                    summary = ask_ai(
                        f"Create {style.lower()} for a Class 10 CBSE student. "
                        "Use clear headings and bullet points. Preserve "
                        "important facts and do not invent information.\n\n"
                        + notes
                    )
                    st.session_state.latest_summary = summary

                except Exception as error:
                    st.error(
                        f"Summarizer error: {type(error).__name__}: {error}"
                    )

    if st.session_state.latest_summary:
        st.markdown("### 📖 Your revision notes")
        st.markdown(st.session_state.latest_summary)

        if st.button("💾 Save summary to My Library"):
            data = load_data()
            data["summaries"].append({
                "title": notes.strip().splitlines()[0][:80]
                if notes.strip() else "Untitled summary",
                "content": st.session_state.latest_summary,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            save_data(data)
            st.success("Summary saved!")


# ---------------- QUIZ STUDIO ----------------
elif page == "🧠 Quiz Studio":
    st.subheader("🧠 Quiz Studio")
    st.write("Create a quiz, answer the questions, and see your results.")

    with st.form("quiz_setup"):
        topic = st.text_input(
            "Quiz topic",
            placeholder="e.g. Electricity or quadratic equations",
        )

        col1, col2 = st.columns(2)

        with col1:
            difficulty = st.selectbox(
                "Difficulty", ["Easy", "Medium", "Hard"]
            )

        with col2:
            count = st.selectbox("Number of questions", [5, 10, 15])

        generate = st.form_submit_button(
            "✨ Generate quiz", use_container_width=True
        )

    if generate:
        if not topic.strip():
            st.warning("Enter a topic first.")
        else:
            with st.spinner("Creating your quiz..."):
                try:
                    st.session_state.quiz = create_quiz(
                        topic.strip(), difficulty, count
                    )
                    st.session_state.quiz_result = None

                except Exception as error:
                    st.error(
                        f"Quiz error: {type(error).__name__}: {error}"
                    )

    quiz = st.session_state.quiz

    if quiz:
        st.markdown(f"### 📘 {quiz['topic']}")

        if st.session_state.quiz_result is None:
            with st.form("answer_quiz"):
                answers = []

                for i, question in enumerate(quiz["questions"]):
                    st.markdown(
                        f"**Question {i + 1}. {question['question']}**"
                    )

                    choice = st.radio(
                        f"Choose your answer for question {i + 1}",
                        question["options"],
                        index=None,
                        key=f"quiz_answer_{i}",
                        label_visibility="collapsed",
                    )

                    answers.append(choice)
                    st.divider()

                submitted = st.form_submit_button(
                    "✅ Submit answers", use_container_width=True
                )

            if submitted:
                unanswered = [
                    i + 1 for i, answer in enumerate(answers)
                    if answer is None
                ]

                if unanswered:
                    st.warning(
                        "Please answer every question. Missing: "
                        + ", ".join(map(str, unanswered))
                    )
                else:
                    correct = sum(
                        answer == question["options"][question["answer"]]
                        for question, answer in zip(
                            quiz["questions"], answers
                        )
                    )

                    total = len(quiz["questions"])
                    percentage = round(correct / total * 100)

                    st.session_state.quiz_result = {
                        "answers": answers,
                        "correct": correct,
                        "total": total,
                        "percentage": percentage,
                    }

                    data = load_data()
                    data["quiz_results"].append({
                        "topic": quiz["topic"],
                        "correct": correct,
                        "total": total,
                        "percentage": percentage,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })
                    save_data(data)
                    st.rerun()

        result = st.session_state.quiz_result

        if result:
            st.markdown("### 🏆 Your results")
            st.metric(
                "Your score",
                f"{result['correct']} / {result['total']}",
                f"{result['percentage']}%",
            )

            if result["percentage"] >= 80:
                st.success("Excellent work! Keep it up! 🎉")
            elif result["percentage"] >= 50:
                st.info("Good effort! Review the explanations below.")
            else:
                st.warning("Keep practising. Every attempt helps you learn!")

            for i, question in enumerate(quiz["questions"]):
                correct_answer = question["options"][question["answer"]]
                user_answer = result["answers"][i]

                if user_answer == correct_answer:
                    st.success(f"Q{i + 1}: Correct!")
                else:
                    st.error(
                        f"Q{i + 1}: Correct answer: {correct_answer}"
                    )

                st.write(question.get("explanation", ""))

            if st.button("🔄 Create another quiz"):
                st.session_state.quiz = None
                st.session_state.quiz_result = None
                st.rerun()


# ---------------- MY LIBRARY ----------------
elif page == "📚 My Library":
    st.subheader("📚 My Library")
    st.write("Your saved revision summaries.")

    summaries = list(reversed(load_data()["summaries"]))

    if not summaries:
        st.info("You haven't saved any summaries yet. Create one first!")
    else:
        for item in summaries:
            with st.expander(
                f"📄 {item['title']} — {item['date']}"
            ):
                st.markdown(item["content"])


# ---------------- MY PROGRESS ----------------
elif page == "📊 My Progress":
    st.subheader("📊 My Progress")
    st.write("Review your saved quiz results and learning history.")

    results = list(reversed(load_data()["quiz_results"]))

    if not results:
        st.info("Complete a quiz to start tracking your progress.")
    else:
        for item in results:
            with st.container(border=True):
                st.markdown(f"**📘 {item['topic']}**")
                st.write(
                    f"Date: {item['date']} | "
                    f"Score: {item['correct']}/{item['total']} | "
                    f"Percentage: {item['percentage']}%"
                )
                st.progress(item["percentage"] / 100)


# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    STUDYMATE AI · MADE FOR CURIOUS MINDS 🎓<br>
    Keep learning. Keep growing.
</div>
""", unsafe_allow_html=True)


# ---------------- FOUNDERS ----------------
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h2 style="color: #FFD700;">Meet Our Founders</h2>
    <p style="color: #FFD700;">
        Built with ambition. Powered by AI. Designed for students.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

founders = [
    ("Arjun Panchal", "Co-Founder"),
    ("Swwara Acharya", "Co-Founder"),
    ("Tanbi Mondal", "Co-Founder"),
]

for col, (name, role) in zip([col1, col2, col3], founders):
    with col:
        st.markdown(
            f"""
            <div class="founder">
                <div style="font-size: 28px;">👤</div>
                <h3>{name}</h3>
                <p>{role}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("""
<div style="text-align: center; color: #FFD700;
            font-size: 12px; margin-top: 24px;">
    © 2026 StudyMate AI
</div>
""", unsafe_allow_html=True)
