
import json
import os
import time
from datetime import datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from google import genai


# =========================================================
# APP CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "studymate_data.json"
MODEL_NAME = "gemini-2.5-flash"
FOCUS_DURATION = 40 * 60


# =========================================================
# SESSION STATE
# =========================================================
DEFAULT_STATE = {
    "page": "🏠 Dashboard",
    "chat_history": [],
    "latest_summary": "",
    "summary_notes": "",
    "quiz": None,
    "quiz_result": None,
    "focus_paused": True,
    "focus_start_time": None,
    "focus_remaining": FOCUS_DURATION,
    "focus_reminder_pending": False,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# BOOK LOGO
# =========================================================
BOOK_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"
     role="img" aria-label="StudyMate AI book logo">
  <defs>
    <linearGradient id="bookGradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#D8BB7A"/>
      <stop offset="100%" stop-color="#45C995"/>
    </linearGradient>
  </defs>
  <circle cx="60" cy="60" r="56" fill="#102A22"/>
  <g fill="none" stroke="url(#bookGradient)" stroke-width="4"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="M60 46 C48 36 34 36 23 41 L23 78 C36 73 49 75 60 85 Z"/>
    <path d="M60 46 C72 36 86 36 97 41 L97 78 C84 73 71 75 60 85 Z"/>
    <path d="M60 46 L60 85"/>
    <path d="M32 51 L46 51"/>
    <path d="M32 61 L46 61"/>
    <path d="M74 51 L88 51"/>
    <path d="M74 61 L88 61"/>
  </g>
  <path d="M60 15 L63 23 L71 26 L63 29 L60 37
           L57 29 L49 26 L57 23 Z"
        fill="#D8BB7A"/>
</svg>
"""


def logo_html(css_class=""):
    return f'<div class="{css_class}">{BOOK_LOGO}</div>'


# =========================================================
# GREEN AND GOLD DESIGN
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --green: #45C995;
        --gold: #D8BB7A;
        --text: #E5F1EA;
        --muted: #A9BCB2;
    }

    .stApp {
        background:
            radial-gradient(ellipse at top left,
                rgba(69,201,149,.09), transparent 40%),
            linear-gradient(180deg, #09140F 0%, #0C1912 100%);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10251F, #09140F);
        border-right: 1px solid rgba(216,187,122,.22);
    }

    h1, h2, h3 {
        color: var(--text);
        letter-spacing: -.4px;
    }

    p, label, .stMarkdown {
        color: var(--text);
    }

    .sidebar-brand {
        text-align: center;
        padding: 12px 4px 20px;
    }

    .sidebar-brand h2 {
        color: var(--text);
        margin: 10px 0 2px;
        font-size: 25px;
    }

    .sidebar-brand p {
        color: var(--muted);
        font-size: 10px;
        letter-spacing: 2px;
    }

    .sidebar-logo svg {
        width: 94px;
        height: 94px;
    }

    .hero {
        padding: 36px 24px;
        margin: 4px 0 26px;
        text-align: center;
        border: 1px solid rgba(216,187,122,.28);
        border-radius: 24px;
        background:
            radial-gradient(circle at top,
                rgba(69,201,149,.14), transparent 65%),
            linear-gradient(135deg, #102A22, #0C1912);
        box-shadow: 0 12px 40px rgba(0,0,0,.15);
    }

    .hero svg {
        width: 106px;
        height: 106px;
        margin-bottom: 12px;
    }

    .hero .eyebrow, .section-eyebrow {
        color: var(--gold);
        font-size: 11px;
        letter-spacing: 2.5px;
        font-weight: 700;
    }

    .hero h1 {
        font-size: clamp(32px, 5vw, 54px);
        margin: 8px 0;
        color: var(--text);
    }

    .hero h2 {
        color: var(--green);
        font-size: clamp(20px, 3vw, 28px);
        margin: 0 0 14px;
    }

    .hero p {
        color: var(--muted);
        max-width: 680px;
        margin: 0 auto;
        line-height: 1.8;
    }

    .metric-card {
        background: linear-gradient(135deg, #16352A, #10251F);
        border: 1px solid rgba(69,201,149,.24);
        border-radius: 18px;
        padding: 22px 16px;
        min-height: 116px;
    }

    .metric-label {
        font-size: 10px;
        color: var(--muted);
        letter-spacing: 1.5px;
        font-weight: 700;
    }

    .metric-value {
        font-size: 34px;
        font-weight: 750;
        color: var(--gold);
        margin-top: 12px;
    }

    .founder {
        background: linear-gradient(145deg, #16352A, #10251F);
        border: 1px solid rgba(216,187,122,.24);
        border-radius: 18px;
        padding: 24px 12px;
        text-align: center;
        min-height: 150px;
    }

    .founder-avatar {
        display: inline-flex;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        align-items: center;
        justify-content: center;
        background: #102A22;
        color: var(--gold);
        border: 1px solid rgba(216,187,122,.4);
        font-size: 22px;
    }

    .founder h3 {
        font-size: 17px;
        margin: 12px 0 4px;
    }

    .founder p {
        color: var(--green);
        font-size: 12px;
    }

    .footer {
        text-align: center;
        color: #A9BCB2;
        font-size: 12px;
        padding: 22px 0;
        line-height: 1.8;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 12px;
        border: 1px solid rgba(69,201,149,.35);
        background: linear-gradient(135deg, #45C995, #21875F);
        color: #07140E;
        font-weight: 700;
        transition: .2s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        border-color: var(--gold);
        color: #07140E;
        filter: brightness(1.08);
    }

    div[data-testid="stMetric"] {
        background: #10251F;
        padding: 14px;
        border-radius: 14px;
        border: 1px solid rgba(69,201,149,.2);
    }

    div[data-testid="stExpander"] {
        border-color: rgba(69,201,149,.25);
        border-radius: 12px;
    }

    hr {
        border-color: rgba(216,187,122,.2);
    }
    /* Keep typed questions readable in white chat/input boxes */
    .stApp input,
    .stApp textarea,
    .stApp [data-baseweb="input"] input,
    .stApp [data-baseweb="textarea"] textarea,
    .stApp [data-testid="stChatInput"] textarea,
    .stApp [data-testid="stChatInput"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
    }

    .stApp input::placeholder,
    .stApp textarea::placeholder,
    .stApp [data-testid="stChatInput"] textarea::placeholder {
        color: #555555 !important;
        -webkit-text-fill-color: #555555 !important;
        opacity: 1 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATA STORAGE
# =========================================================
def empty_data():
    return {
        "summaries": [],
        "quiz_results": [],
    }


def load_data():
    """Load saved summaries and quiz results."""
    if not os.path.exists(DATA_FILE):
        return empty_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return empty_data()

        if not isinstance(data.get("summaries"), list):
            data["summaries"] = []

        if not isinstance(data.get("quiz_results"), list):
            data["quiz_results"] = []

        return data

    except (OSError, json.JSONDecodeError):
        return empty_data()


def save_data(data):
    """Save application data to JSON."""
    temporary_file = DATA_FILE + ".tmp"

    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    os.replace(temporary_file, DATA_FILE)


# =========================================================
# GEMINI AI
# =========================================================
def get_gemini_client():
    """Create the Gemini client using Streamlit Secrets."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key or not str(api_key).strip():
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Open Streamlit Cloud settings, "
            "go to Secrets, and configure your Gemini API key."
        )

    return genai.Client(api_key=str(api_key).strip())


def ask_ai(prompt, system_prompt=None):
    """Send a prompt to Gemini and return its answer."""
    if system_prompt is None:
        system_prompt = (
            "You are StudyMate AI, a helpful tutor for Class 10 CBSE students. "
            "Explain concepts clearly, use accurate information and examples, "
            "show working for mathematics, and admit uncertainty when needed."
        )

    response = get_gemini_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"system_instruction": system_prompt},
    )

    answer = response.text

    if not answer or not answer.strip():
        raise RuntimeError("Gemini returned an empty response. Please try again.")

    return answer.strip()


# =========================================================
# QUIZ GENERATION
# =========================================================
def create_quiz(topic, difficulty, count):
    """Generate and validate multiple-choice questions."""
    prompt = f"""
Create exactly {count} multiple-choice questions about "{topic}"
for a Class 10 CBSE student.

Difficulty: {difficulty}.

Return only valid JSON in this format:
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

Rules:
- Generate exactly {count} questions.
- Every question must have exactly four options.
- The answer must be the zero-based index of the correct option.
- Each question must have one correct answer.
- Explanations should be clear and accurate.
- Do not include Markdown fences or text outside the JSON.
"""

    response = get_gemini_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "system_instruction": (
                "You create accurate educational quizzes for Class 10 CBSE. "
                "Return valid JSON only."
            ),
            "response_mime_type": "application/json",
        },
    )

    content = response.text

    if not content or not content.strip():
        raise RuntimeError("Gemini returned an empty quiz. Please try again.")

    try:
        quiz_data = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The generated quiz was not valid JSON. Please try again."
        ) from error

    questions = quiz_data.get("questions")

    if not isinstance(questions, list) or len(questions) != count:
        raise ValueError(
            f"The quiz must contain exactly {count} questions. Please retry."
        )

    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("A generated quiz question has an invalid format.")

        options = question.get("options")
        answer = question.get("answer")

        if (
            not isinstance(question.get("question"), str)
            or not isinstance(options, list)
            or len(options) != 4
            or not all(isinstance(option, str) for option in options)
            or not isinstance(answer, int)
            or isinstance(answer, bool)
            or answer not in range(4)
        ):
            raise ValueError(
                "A generated quiz question has an invalid format."
            )

        question.setdefault(
            "explanation",
            "Review this concept in your notes.",
        )

    return {"topic": topic, "questions": questions}


# =========================================================
# NAVIGATION
# =========================================================
def go_to_page(page_name):
    st.session_state.page = page_name


# =========================================================
# FOCUS TIMER FUNCTIONS
# =========================================================
def focus_seconds_remaining():
    """Calculate the current timer value."""
    if st.session_state.focus_paused:
        return max(0, int(st.session_state.focus_remaining))

    started = st.session_state.focus_start_time

    if started is None:
        return max(0, int(st.session_state.focus_remaining))

    elapsed = time.time() - started
    return max(0, int(st.session_state.focus_remaining - elapsed))


def start_focus():
    st.session_state.focus_remaining = FOCUS_DURATION
    st.session_state.focus_start_time = time.time()
    st.session_state.focus_paused = False
    st.session_state.focus_reminder_pending = False


def pause_focus():
    remaining = focus_seconds_remaining()
    st.session_state.focus_remaining = remaining
    st.session_state.focus_start_time = None
    st.session_state.focus_paused = True


def resume_focus():
    st.session_state.focus_start_time = time.time()
    st.session_state.focus_paused = False


def finish_focus_if_needed():
    if (
        not st.session_state.focus_paused
        and focus_seconds_remaining() <= 0
    ):
        st.session_state.focus_remaining = 0
        st.session_state.focus_start_time = None
        st.session_state.focus_paused = True
        st.session_state.focus_reminder_pending = True


finish_focus_if_needed()

if not st.session_state.focus_paused:
    st_autorefresh(interval=1000, key="focus_timer_refresh")


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            {logo_html("sidebar-logo")}
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

    st.radio(
        "YOUR WORKSPACE",
        page_options,
        key="page",
    )

    st.divider()
    st.markdown("### ⏳ Focus Mode")

    remaining = focus_seconds_remaining()
    minutes, seconds = divmod(remaining, 60)

    if st.session_state.focus_reminder_pending:
        st.success("Your 40-minute session is complete!")

    elif st.session_state.focus_paused:
        st.info("Timer paused.")

    else:
        st.markdown(
            f"**Time remaining: {minutes:02d}:{seconds:02d}**"
        )
        st.progress(
            max(
                0.0,
                min(1.0, remaining / FOCUS_DURATION),
            )
        )

    if st.session_state.focus_paused:
        if st.session_state.focus_remaining == FOCUS_DURATION:
            if st.button(
                "▶️ Start 40-minute session",
                use_container_width=True,
                key="start_focus",
            ):
                start_focus()
                st.rerun()
        else:
            if st.button(
                "▶️ Resume focus session",
                use_container_width=True,
                key="resume_focus",
            ):
                resume_focus()
                st.rerun()

            if st.button(
                "🔄 Restart timer",
                use_container_width=True,
                key="restart_focus",
            ):
                start_focus()
                st.rerun()

    else:
        if st.button(
            "⏸️ Pause timer",
            use_container_width=True,
            key="pause_focus",
        ):
            pause_focus()
            st.rerun()

    st.divider()
    st.caption("✦ Powered by Gemini AI")
    st.caption("Built for curious minds.")


page = st.session_state.page


# =========================================================
# FOCUS REMINDER
# =========================================================
quiz_in_progress = (
    page == "🧠 Quiz Studio"
    and st.session_state.quiz is not None
    and st.session_state.quiz_result is None
)

if st.session_state.focus_reminder_pending and not quiz_in_progress:

    @st.dialog("🌱 Time for a Focus Check-in!")
    def focus_reminder():
        st.markdown(
            """
            <div style="
                background:linear-gradient(135deg,#102A22,#174B38);
                border:1px solid #D8BB7A;
                border-radius:16px;
                padding:24px;
                text-align:center;">
                <div style="font-size:42px;">🎓</div>
                <h2 style="color:#D8BB7A;">40 minutes. Great effort!</h2>
                <p style="color:#E5F1EA;">
                    You have completed a focus session.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("Take a moment to rest your eyes and stretch.")

        if st.button("✅ Continue studying", use_container_width=True):
            st.session_state.focus_reminder_pending = False
            st.session_state.focus_remaining = FOCUS_DURATION
            st.session_state.focus_start_time = time.time()
            st.session_state.focus_paused = False
            st.rerun()

        if st.button("☕ Take a short break", use_container_width=True):
            st.session_state.focus_reminder_pending = False
            st.session_state.focus_remaining = FOCUS_DURATION
            st.session_state.focus_start_time = None
            st.session_state.focus_paused = True
            st.rerun()

    focus_reminder()


# =========================================================
# MAIN HEADER
# =========================================================
st.markdown(
    f"""
    <div class="hero">
        {logo_html()}
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


# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":
    st.subheader("Welcome to your study space 👋")
    st.write("What would you like to work on today?")

    data = load_data()
    total_quizzes = len(data["quiz_results"])
    saved_notes = len(data["summaries"])

    average = (
        sum(
            result.get("percentage", 0)
            for result in data["quiz_results"]
        ) / total_quizzes
        if total_quizzes
        else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">QUIZZES COMPLETED</div>
                <div class="metric-value">{total_quizzes}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">SAVED SUMMARIES</div>
                <div class="metric-value">{saved_notes}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">AVERAGE QUIZ SCORE</div>
                <div class="metric-value">{average:.0f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### ✨ Your study tools")

    a, b, c = st.columns(3)

    with a:
        with st.container(border=True):
            st.markdown("### 💬")
            st.markdown("**Study Chat**")
            st.write("Understand difficult concepts with your AI tutor.")
            st.button(
                "Open Study Chat",
                use_container_width=True,
                on_click=go_to_page,
                args=("💬 Study Chat",),
                key="open_study_chat",
            )

    with b:
        with st.container(border=True):
            st.markdown("### 📝")
            st.markdown("**Smart Summarizer**")
            st.write("Turn long notes into organised revision points.")
            st.button(
                "Open Summarizer",
                use_container_width=True,
                on_click=go_to_page,
                args=("📝 Summarizer",),
                key="open_summarizer",
            )

    with c:
        with st.container(border=True):
            st.markdown("### 🧠")
            st.markdown("**Quiz Studio**")
            st.write("Generate questions, test your knowledge, and check your score.")
            st.button(
                "Open Quiz Studio",
                use_container_width=True,
                on_click=go_to_page,
                args=("🧠 Quiz Studio",),
                key="open_quiz_studio",
            )

    st.markdown("### 🌱 Study tip")
    st.info(
        "Study one topic, make a short summary, and test your understanding "
        "with a quiz. Small, consistent steps can make revision easier."
    )


# =========================================================
# STUDY CHAT
# =========================================================
elif page == "💬 Study Chat":
    st.subheader("💬 Study Chat")
    st.write("Ask questions and learn at your own pace.")

    if not st.session_state.chat_history:
        st.markdown(
            """
            <div style="
                background:linear-gradient(135deg,#152B23,#0C1C16);
                border:1px solid rgba(54,220,160,.30);
                border-radius:16px;
                padding:22px;
                margin:16px 0;
                text-align:center;">
                <div style="font-size:38px;">📚</div>
                <h3 style="color:#36DCA0;">Hey there, learner!</h3>
                <p style="color:#C0D1C8;">
                    I'm your StudyMate AI tutor. Ask me anything about
                    your Class 10 CBSE subjects, and we'll work through
                    it together.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
                    history_text = "\n\n".join(
                        f'{message["role"]}: {message["content"]}'
                        for message in st.session_state.chat_history[-12:]
                    )

                    answer = ask_ai(
                        history_text,
                        system_prompt=(
                            "You are StudyMate AI, a friendly and accurate "
                            "Class 10 CBSE tutor. Answer the student's latest "
                            "question clearly. Explain step by step when useful. "
                            "Use simple explanations and examples. For maths, "
                            "show the working. If a question is ambiguous, "
                            "ask for clarification. Do not invent facts."
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

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_study_chat"):
            st.session_state.chat_history = []
            st.rerun()


# =========================================================
# SMART SUMMARIZER
# =========================================================
elif page == "📝 Summarizer":
    st.subheader("📝 Smart Summarizer")
    st.write("Turn your study material into clear revision notes.")

    notes = st.text_area(
        "Paste your notes",
        height=220,
        placeholder="Paste your textbook notes here...",
        key="summary_notes",
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

    if st.button(
        "✨ Summarize notes",
        use_container_width=True,
        key="summarize_notes_button",
    ):
        if not notes.strip():
            st.warning("Paste your notes first.")

        else:
            with st.spinner("Organising your notes..."):
                try:
                    summary = ask_ai(
                        f"""
Create {style.lower()} for a Class 10 CBSE student.

Instructions:
- Use clear headings and bullet points.
- Preserve important facts and definitions.
- Do not invent information not supported by the notes.
- Keep the summary useful for revision.

STUDY NOTES:
{notes}
"""
                    )
                    st.session_state.latest_summary = summary
                    st.session_state.summary_notes = notes

                except Exception as error:
                    st.error(
                        f"Summarizer error: {type(error).__name__}: {error}"
                    )

    if st.session_state.latest_summary:
        st.markdown("### 📖 Your revision notes")
        st.markdown(st.session_state.latest_summary)

        if st.button("💾 Save summary to My Library", key="save_summary"):
            data = load_data()

            data["summaries"].append(
                {
                    "title": (
                        st.session_state.summary_notes.strip().splitlines()[0][:80]
                        if st.session_state.summary_notes.strip()
                        else "Untitled summary"
                    ),
                    "content": st.session_state.latest_summary,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

            try:
                save_data(data)
                st.success("Summary saved to My Library!")
            except OSError as error:
                st.error(f"Could not save the summary: {error}")


# =========================================================
# QUIZ STUDIO
# =========================================================
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
                "Difficulty",
                ["Easy", "Medium", "Hard"],
            )

        with col2:
            count = st.selectbox(
                "Number of questions",
                [5, 10, 15],
            )

        generate = st.form_submit_button(
            "✨ Generate quiz",
            use_container_width=True,
        )

    if generate:
        if not topic.strip():
            st.warning("Enter a topic first.")

        else:
            with st.spinner("Creating your quiz..."):
                try:
                    st.session_state.quiz = create_quiz(
                        topic.strip(),
                        difficulty,
                        count,
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
                    "✅ Submit answers",
                    use_container_width=True,
                )

            if submitted:
                unanswered = [
                    i + 1
                    for i, answer in enumerate(answers)
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
                            quiz["questions"],
                            answers,
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
                    data["quiz_results"].append(
                        {
                            "topic": quiz["topic"],
                            "correct": correct,
                            "total": total,
                            "percentage": percentage,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    )

                    try:
                        save_data(data)
                    except OSError as error:
                        st.error(f"Could not save quiz results: {error}")

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

            st.markdown("### 📝 Answer review")

            for i, question in enumerate(quiz["questions"]):
                correct_answer = question["options"][question["answer"]]
                user_answer = result["answers"][i]

                if user_answer == correct_answer:
                    st.success(f"Question {i + 1}: Correct!")
                else:
                    st.error(
                        f"Question {i + 1}: Correct answer: {correct_answer}"
                    )

                st.write(
                    question.get(
                        "explanation",
                        "Review this topic in your notes.",
                    )
                )

            if st.button("🔄 Create another quiz", key="another_quiz"):
                st.session_state.quiz = None
                st.session_state.quiz_result = None
                st.rerun()


# =========================================================
# MY LIBRARY
# =========================================================
elif page == "📚 My Library":
    st.subheader("📚 My Library")
    st.write("Your saved revision summaries.")

    summaries = list(reversed(load_data()["summaries"]))

    if not summaries:
        st.info("You haven't saved any summaries yet. Create one first!")

    else:
        for index, item in enumerate(summaries):
            title = item.get("title", "Untitled summary")
            date = item.get("date", "Date unavailable")
            content = item.get("content", "")

            with st.expander(f"📄 {title} — {date}"):
                st.markdown(content)

                st.download_button(
                    "⬇️ Download summary",
                    data=content,
                    file_name=f"summary_{index + 1}.txt",
                    mime="text/plain",
                    key=f"download_summary_{index}",
                )


# =========================================================
# MY PROGRESS
# =========================================================
elif page == "📊 My Progress":
    st.subheader("📊 My Progress")
    st.write("Review your saved quiz results and learning history.")

    results = list(reversed(load_data()["quiz_results"]))

    if not results:
        st.info("Complete a quiz to start tracking your progress.")

    else:
        scores = [
            result.get("percentage", 0)
            for result in results
        ]

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Quizzes completed", len(results))

        with col2:
            st.metric(
                "Average score",
                f"{sum(scores) / len(scores):.0f}%",
            )

        for item in results:
            with st.container(border=True):
                st.markdown(
                    f"**📘 {item.get('topic', 'Untitled quiz')}**"
                )

                st.write(
                    f"Date: {item.get('date', 'Unknown')} | "
                    f"Score: {item.get('correct', 0)}/"
                    f"{item.get('total', 0)} | "
                    f"Percentage: {item.get('percentage', 0)}%"
                )

                st.progress(
                    max(
                        0.0,
                        min(
                            1.0,
                            item.get("percentage", 0) / 100,
                        ),
                    )
                )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer">
        STUDYMATE AI · MADE FOR CURIOUS MINDS<br>
        Keep learning. Keep growing.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MEET OUR FOUNDERS
# =========================================================
st.markdown(
    """
    <div style="text-align:center;padding:20px 0 14px;">
        <div class="section-eyebrow">THE PEOPLE BEHIND THE PROJECT</div>
        <h2 style="margin-top:8px;">Meet Our Founders</h2>
        <p style="color:#A9BCB2;">
            Built with ambition. Powered by AI. Designed for students.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
                <div class="founder-avatar">✦</div>
                <h3>{name}</h3>
                <p>{role}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div style="
        text-align:center;
        color:#82998D;
        font-size:12px;
        margin-top:24px;
        padding-bottom:12px;">
        © 2026 StudyMate AI · Learn smarter, every day.
    </div>
    """,
    unsafe_allow_html=True,
)
