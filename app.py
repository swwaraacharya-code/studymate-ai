
import json
import os
from datetime import datetime

import streamlit as st
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
    <path d="M32 51 L46 51 M32 61 L46 61
             M74 51 L88 51 M74 61 L88 61"/>
  </g>
  <g stroke="#E8C985" stroke-width="2.5" fill="#E8C985"
     filter="url(#glow)">
    <path d="M60 14 V24 M55 19 H65"/>
    <circle cx="37" cy="27" r="3"/>
    <circle cx="83" cy="27" r="3"/>
    <circle cx="16" cy="57" r="2"/>
    <circle cx="104" cy="57" r="2"/>
  </g>
  <g stroke="#E8C985" stroke-width="1.5" fill="none">
    <path d="M37 27 L48 37 M83 27 L72 37"/>
    <path d="M16 57 L23 57 M97 57 L104 57"/>
  </g>
</svg>
"""


# =========================================================
# LOCAL DATA
# =========================================================
def load_data():
    """Load saved summaries and quiz results."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("Saved data has an invalid format.")

            data.setdefault("summaries", [])
            data.setdefault("quiz_results", [])

            return data

        except (json.JSONDecodeError, OSError, ValueError):
            pass

    return {
        "summaries": [],
        "quiz_results": [],
    }


def save_data(data):
    """Save summaries and quiz results locally."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


# =========================================================
# SESSION STATE
# =========================================================
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


# =========================================================
# FUTURISTIC DARK UI
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --bg: #07120F;
        --panel: #10201B;
        --panel-light: #152B24;
        --emerald: #36DCA0;
        --emerald-dark: #087F5B;
        --gold: #D8BB7A;
        --text: #F1F7F3;
        --muted: #A9BCB2;
        --border: rgba(94, 180, 139, 0.24);
    }

    .stApp {
        background:
            radial-gradient(
                circle at 15% 8%,
                rgba(24, 115, 78, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 35%,
                rgba(200, 169, 110, 0.07),
                transparent 27%
            ),
            #07120F;
        color: var(--text);
        font-family: "Segoe UI", Arial, sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(7, 18, 15, 0.85);
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1914, #08110E);
        border-right: 1px solid rgba(54, 220, 160, 0.20);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 10px;
        padding: 8px 10px;
        transition: background 0.2s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(54, 220, 160, 0.10);
    }

    h1, h2, h3, h4, h5 {
        color: var(--text) !important;
        letter-spacing: -0.4px;
    }

    p, li, label, .stMarkdown {
        color: var(--text);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    .sidebar-brand {
        text-align: center;
        padding: 18px 8px 20px;
    }

    .sidebar-logo {
        width: 112px;
        height: 112px;
        margin: 0 auto 8px;
        animation: logoFloat 4s ease-in-out infinite;
        filter: drop-shadow(0 0 14px rgba(54, 220, 160, 0.17));
    }

    .sidebar-brand h2 {
        font-size: 24px;
        font-weight: 800;
        margin: 7px 0 4px;
        color: #F1F7F3 !important;
    }

    .sidebar-brand p {
        font-size: 10px;
        letter-spacing: 2px;
        font-weight: 700;
        color: var(--gold) !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 34px 22px;
        margin: 8px 0 28px;
        background:
            linear-gradient(
                135deg,
                rgba(20, 48, 37, 0.97),
                rgba(10, 25, 20, 0.97)
            );
        border: 1px solid rgba(54, 220, 160, 0.30);
        border-top: 2px solid var(--gold);
        border-radius: 24px;
        box-shadow: 0 14px 45px rgba(0, 0, 0, 0.24);
        animation: fadeUp 0.6s ease both;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        left: -130px;
        top: -170px;
        border-radius: 50%;
        background: rgba(54, 220, 160, 0.10);
        filter: blur(10px);
        pointer-events: none;
    }

    .hero-logo {
        width: 104px;
        height: 104px;
        margin-bottom: 10px;
        filter: drop-shadow(0 0 17px rgba(54, 220, 160, 0.18));
        animation: logoFloat 4s ease-in-out infinite;
    }

    .eyebrow {
        color: var(--gold) !important;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 3px;
        margin-top: 5px;
    }

    .hero h1 {
        color: #F3FBF6 !important;
        font-size: clamp(30px, 5vw, 46px);
        font-weight: 850;
        margin: 8px 0;
        letter-spacing: -1.5px;
    }

    .hero h2 {
        color: var(--emerald) !important;
        font-size: clamp(17px, 2.5vw, 22px);
        font-weight: 700;
        margin: 8px 0 12px;
    }

    .hero p {
        color: #C0D1C8 !important;
        font-size: 15px;
        line-height: 1.8;
        max-width: 720px;
        margin: 0 auto;
    }

    .feature,
    .metric-card,
    .founder {
        background: linear-gradient(
            145deg,
            rgba(21, 43, 35, 0.98),
            rgba(12, 28, 22, 0.98)
        );
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        transition:
            transform 0.22s ease,
            border-color 0.22s ease,
            box-shadow 0.22s ease;
    }

    .feature:hover,
    .founder:hover {
        transform: translateY(-4px);
        border-color: rgba(54, 220, 160, 0.65);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.24);
    }

    .metric-card {
        min-height: 125px;
        border-top: 2px solid var(--emerald);
    }

    .metric-label {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.4px;
        color: var(--muted);
    }

    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: var(--emerald);
        margin-top: 12px;
    }

    .st-key-study_chat_card,
    .st-key-summarizer_card,
    .st-key-quiz_studio_card {
        background: linear-gradient(
            145deg,
            rgba(21, 43, 35, 0.98),
            rgba(12, 28, 22, 0.98)
        ) !important;
        border: 1px solid var(--border) !important;
        border-radius: 18px !important;
        padding: 20px !important;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }

    .st-key-study_chat_card:hover,
    .st-key-summarizer_card:hover,
    .st-key-quiz_studio_card:hover {
        border-color: var(--emerald) !important;
        transform: translateY(-2px);
    }

    .st-key-study_chat_card *,
    .st-key-summarizer_card *,
    .st-key-quiz_studio_card * {
        color: var(--text);
    }

    .st-key-study_chat_card h3,
    .st-key-summarizer_card h3,
    .st-key-quiz_studio_card h3 {
        color: var(--emerald) !important;
    }

    .founder {
        text-align: center;
        padding: 24px 12px;
        min-height: 145px;
    }

    .founder h3 {
        color: var(--text) !important;
        font-size: 17px;
    }

    .founder p {
        color: var(--gold) !important;
        font-size: 13px;
    }

    .founder-avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 52px;
        height: 52px;
        margin-bottom: 10px;
        border-radius: 50%;
        border: 1px solid rgba(216, 187, 122, 0.5);
        background: rgba(54, 220, 160, 0.10);
        font-size: 25px;
    }

    /* Buttons use dark text for clear contrast. */
    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #42E5AA, #23B985) !important;
        color: #07120F !important;
        border: 1px solid #42E5AA !important;
        border-radius: 10px !important;
        min-height: 42px;
        padding: 9px 18px;
        font-weight: 800 !important;
        transition: transform 0.2s ease, filter 0.2s ease;
    }

    .stButton > button *,
    .stFormSubmitButton > button * {
        color: #07120F !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
    }

    .stButton > button:focus,
    .stFormSubmitButton > button:focus {
        box-shadow: 0 0 0 3px rgba(54, 220, 160, 0.22) !important;
    }

    /* Text fields */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stChatInput"] textarea {
        background: #0B1914 !important;
        color: #F1F7F3 !important;
        border: 1px solid rgba(54, 220, 160, 0.30) !important;
        border-radius: 11px !important;
        caret-color: var(--emerald);
    }

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder,
    [data-testid="stChatInput"] textarea::placeholder {
        color: #82998D !important;
    }

    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stMultiSelect"] div[data-baseweb="select"] {
        background: #0B1914;
        color: #F1F7F3;
        border-radius: 10px;
    }

    [data-testid="stSelectbox"] *,
    [data-testid="stMultiSelect"] * {
        color: #F1F7F3;
    }

    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label {
        color: var(--text) !important;
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(16, 32, 27, 0.90);
        border: 1px solid rgba(94, 180, 139, 0.20);
        border-radius: 15px;
        padding: 14px;
        margin-bottom: 10px;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3 {
        color: #F1F7F3 !important;
    }

    [data-testid="stChatInput"] {
        border: 1px solid rgba(54, 220, 160, 0.45);
        border-radius: 14px;
        background: #0B1914;
    }

    [data-testid="stChatInput"] button {
        color: #36DCA0 !important;
    }

    /* Expanders and forms */
    [data-testid="stExpander"] {
        background: rgba(16, 32, 27, 0.92);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stExpander"] * {
        color: var(--text);
    }

    [data-testid="stForm"] {
        background: rgba(16, 32, 27, 0.55);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 18px;
    }

    [data-testid="stMetric"] {
        background: rgba(16, 32, 27, 0.65);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 12px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: var(--text) !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: rgba(94, 180, 139, 0.22);
    }

    .footer {
        text-align: center;
        padding: 22px 10px 8px;
        color: #9DB4A8;
        font-size: 12px;
        letter-spacing: 0.4px;
    }

    .section-eyebrow {
        color: var(--gold);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
    }

    @keyframes logoFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    @media (max-width: 640px) {
        .hero {
            padding: 26px 15px;
        }

        .hero-logo {
            width: 84px;
            height: 84px;
        }

        .sidebar-logo {
            width: 90px;
            height: 90px;
        }

        .metric-value {
            font-size: 25px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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

    st.caption("✦ Powered by Gemini AI")
    st.caption("Built for curious minds.")


page = st.session_state.page


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
        with st.container(border=True, key="study_chat_card"):
            st.markdown("### 💬")
            st.markdown("**Study Chat**")
            st.write(
                "Understand difficult concepts with your AI tutor."
            )
            st.button(
                "Open Study Chat",
                use_container_width=True,
                on_click=go_to_page,
                args=("💬 Study Chat",),
                key="open_study_chat",
            )

    with b:
        with st.container(border=True, key="summarizer_card"):
            st.markdown("### 📝")
            st.markdown("**Smart Summarizer**")
            st.write(
                "Turn long notes into organised revision points."
            )
            st.button(
                "Open Summarizer",
                use_container_width=True,
                on_click=go_to_page,
                args=("📝 Summarizer",),
                key="open_summarizer",
            )

    with c:
        with st.container(border=True, key="quiz_studio_card"):
            st.markdown("### 🧠")
            st.markdown("**Quiz Studio**")
            st.write(
                "Generate questions, test your knowledge, and check your score."
            )
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
                background: linear-gradient(
                    135deg,
                    rgba(21, 43, 35, .98),
                    rgba(12, 28, 22, .98)
                );
                border: 1px solid rgba(54, 220, 160, .30);
                border-radius: 16px;
                padding: 22px;
                margin: 16px 0;
                text-align: center;
            ">
                <div style="font-size: 38px;">📚</div>
                <h3 style="color: #36DCA0;">
                    Hey there, learner!
                </h3>
                <p style="color: #C0D1C8;">
                    I'm your StudyMate AI tutor. Ask me anything about
                    your Class 10 CBSE subjects, and we'll work through
                    it together.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Display previous chat messages.
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Keep the question input box.
    question = st.chat_input(
        "Ask a question about Maths, Science, English..."
    )

    if question:
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
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
                        {
                            "role": "assistant",
                            "content": answer,
                        }
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
        if st.button(
            "🗑️ Clear Chat",
            key="clear_study_chat",
        ):
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
""",
                    )

                    st.session_state.latest_summary = summary

                except Exception as error:
                    st.error(
                        f"Summarizer error: {type(error).__name__}: {error}"
                    )

    if st.session_state.latest_summary:
        st.markdown("### 📖 Your revision notes")
        st.markdown(st.session_state.latest_summary)

        if st.button(
            "💾 Save summary to My Library",
            key="save_summary",
        ):
            data = load_data()

            data["summaries"].append(
                {
                    "title": (
                        notes.strip().splitlines()[0][:80]
                        if notes.strip()
                        else "Untitled summary"
                    ),
                    "content": st.session_state.latest_summary,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

            save_data(data)
            st.success("Summary saved to My Library!")


# =========================================================
# QUIZ STUDIO
# =========================================================
elif page == "🧠 Quiz Studio":
    st.subheader("🧠 Quiz Studio")
    st.write(
        "Create a quiz, answer the questions, and see your results."
    )

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
                            "date": datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                        }
                    )

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
                st.info(
                    "Good effort! Review the explanations below."
                )
            else:
                st.warning(
                    "Keep practising. Every attempt helps you learn!"
                )

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

                explanation = question.get(
                    "explanation",
                    "Review this topic in your notes.",
                )

                st.write(explanation)

            if st.button(
                "🔄 Create another quiz",
                key="another_quiz",
            ):
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
        st.info(
            "You haven't saved any summaries yet. Create one first!"
        )

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
        st.info(
            "Complete a quiz to start tracking your progress."
        )

    else:
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
    <div style="text-align: center; padding: 20px 0 14px;">
        <div class="section-eyebrow">THE PEOPLE BEHIND THE PROJECT</div>
        <h2 style="margin-top: 8px;">Meet Our Founders</h2>
        <p style="color: #A9BCB2;">
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
        text-align: center;
        color: #82998D;
        font-size: 12px;
        margin-top: 24px;
        padding-bottom: 12px;
    ">
        © 2026 StudyMate AI · Learn smarter, every day.
    </div>
    """,
    unsafe_allow_html=True,
)
