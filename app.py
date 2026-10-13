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

# Use a model available to your Gemini API key.
MODEL_NAME = "gemini-2.5-flash"

FOCUS_DURATION = 40 * 60  # 40 minutes, in seconds


# =========================================================
# INTELLIGENT BOOK BRAND MARK
# =========================================================
BOOK_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"
     role="img" aria-label="StudyMate AI intelligent book logo">
  <defs>
    <linearGradient id="bookGradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#38E6A3"/>
      <stop offset="100%" stop-color="#087F5B"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <circle cx="60" cy="60" r="54" fill="#10251F"
          stroke="#C9A96E" stroke-opacity=".55"/>
  <g fill="none" stroke="url(#bookGradient)" stroke-width="4"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="M60 46 C48 36 34 36 23 41 L23 78
             C36 73 49 75 60 85 Z"/>
    <path d="M60 46 C72 36 86 36 97 41 L97 78
             C84 73 71 75 60 85 Z"/>
    <path d="M60 46 L60 85"/>
    <path d="M32 51 L46 51 M32
# =========================================================
# LOGO HTML HELPER
# =========================================================
def logo_html(css_class="hero-logo"):
    """Return the custom SVG logo without using the school logo."""
    return f'<div class="{css_class}">{BOOK_LOGO}</div>'


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
            "GEMINI_API_KEY is missing. Open your Streamlit app settings, "
            "go to Secrets, and make sure your Gemini API key is configured."
        )

    return genai.Client(api_key=api_key)


def ask_ai(prompt, system_prompt=None):
    """Send a prompt to Gemini and return the text response."""
    if system_prompt is None:
        system_prompt = (
            "You are StudyMate AI, a helpful tutor for Class 10 CBSE students. "
            "Explain concepts clearly, use accurate information and examples, "
            "show working for mathematics, and admit uncertainty when needed."
        )

    client = get_gemini_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "system_instruction": system_prompt,
        },
    )

    answer = response.text

    if not answer or not answer.strip():
        raise RuntimeError(
            "Gemini returned an empty response. Please try again."
        )

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
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
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

    client = get_gemini_client()

    response = client.models.generate_content(
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

    if not isinstance(questions, list) or len(questions) < 1:
        raise ValueError("The generated quiz format was unexpected.")

    questions = questions[:count]

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

        question.setdefault("explanation", "Review this concept in your notes.")

    return {
        "topic": topic,
        "questions": questions,
    }


# =========================================================
# NAVIGATION
# =========================================================
def go_to_page(page_name):
    st.session_state.page = page_name


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

    # Focus timer display
    st.markdown("### ⏳ Focus Mode")

    if st.session_state.focus_paused:
        st.info("Timer paused — enjoy your break!")
    elif st.session_state.focus_reminder_pending:
        st.success("Your 40-minute session is complete!")
    else:
        remaining = max(
            0,
            int(FOCUS_DURATION - focus_elapsed),
        )
        minutes, seconds = divmod(remaining, 60)

        st.markdown(
            f"**Time until reminder: {minutes:02d}:{seconds:02d}**"
        )
        st.progress(
            min(1.0, focus_elapsed / FOCUS_DURATION)
        )

    st.divider()

    st.caption("✦ Powered by Gemini AI")
    st.caption("Built for curious minds.")


page = st.session_state.page


# =========================================================
# 40-MINUTE FOCUS REMINDER POPUP
# =========================================================
# Do not interrupt a student while they are answering an active quiz.
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
                background: linear-gradient(135deg, #102A22, #174B38);
                border: 1px solid #D8BB7A;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
            ">
                <div style="font-size: 42px;">🎓</div>
                <h2 style="color: #D8BB7A;">
                    40 minutes. Great effort!
                </h2>
                <p style="color: #E5F1EA;">
                    You've completed a focus session.
                    Stretch, drink some water, or take a moment
                    to recharge before your next session.
                </p>
                <p style="color: #D8BB7A;">
                    STUDYMATE AI · KEEP LEARNING. KEEP GROWING.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("What would you like to do next?")

        if st.button(
            "🚀 Continue studying",
            use_container_width=True,
            key="focus_continue",
        ):
            st.session_state.focus_start_time = time.time()
            st.session_state.focus_paused = False
            st.session_state.focus_reminder_pending = False
            st.rerun()

        if st.button(
            "☕ Take a short break",
            use_container_width=True,
            key="focus_take_break",
        ):
            st.session_state.focus_paused = True
            st.session_state.focus_reminder_pending = False
            st.rerun()

    focus_reminder()


# =========================================================
# RESUME FOCUS AFTER A BREAK
# =========================================================
if st.session_state.focus_paused:
    with st.sidebar:
        if st.button(
            "▶️ Resume my focus session",
            use_container_width=True,
            key="resume_focus_session",
        ):
            st.session_state.focus_paused = False
            st.session_state.focus_start_time = time.time()
            st.session_state.focus_reminder_pending = False
            st.rerun()


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
