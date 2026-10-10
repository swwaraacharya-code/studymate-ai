
import streamlit as st
from google import genai
from html import escape

# ==========================================
# STUDYMATE AI — TREE HOUSE HIGH SCHOOL
# ==========================================

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CONFIGURATION ----------
GREEN = "#14532d"
GOLD = "#FFD700"
WHITE = "#FFFFFF"
BLACK = "#000000"

LOGO_URL = (
    "https://treehousehighschool.com/wp-content/uploads/"
    "2025/12/imgi_4_1024.png"
)

# ---------- CUSTOM CSS ----------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {GREEN};
        color: {WHITE};
    }}

    [data-testid="stHeader"] {{
        background-color: {GREEN};
    }}

    [data-testid="stSidebar"] {{
        background-color: #0b3b20;
    }}

    [data-testid="stSidebar"] * {{
        color: {WHITE};
    }}

    h1, h2, h3 {{
        color: {GOLD} !important;
        font-weight: 800 !important;
    }}

    p, label, .stMarkdown, .stCaption {{
        color: {WHITE};
    }}

    /* Dashboard buttons — BLACK TEXT */
    div.stButton > button {{
        background-color: {GOLD} !important;
        color: {BLACK} !important;
        border: 2px solid {GOLD} !important;
        border-radius: 12px !important;
        min-height: 54px;
        font-size: 16px !important;
        font-weight: 800 !important;
        width: 100%;
        transition: 0.2s ease;
    }}

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {{
        color: {BLACK} !important;
        font-weight: 800 !important;
    }}

    div.stButton > button:hover {{
        background-color: #ffffff !important;
        border-color: #ffffff !important;
        color: {BLACK} !important;
        transform: translateY(-2px);
    }}

    div.stButton > button:hover p,
    div.stButton > button:hover span {{
        color: {BLACK} !important;
    }}

    /* Text inputs and text areas */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {{
        background-color: {WHITE} !important;
        color: {BLACK} !important;
        -webkit-text-fill-color: {BLACK} !important;
        caret-color: {BLACK} !important;
        border-radius: 8px !important;
    }}

    /* STUDY CHAT — MESSAGE BOX TEXT IN BLACK */
    [data-testid="stChatInput"] {{
        background-color: {WHITE} !important;
        border: 2px solid {GOLD} !important;
        border-radius: 12px !important;
    }}

    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] textarea:focus {{
        color: {BLACK} !important;
        -webkit-text-fill-color: {BLACK} !important;
        caret-color: {BLACK} !important;
        background-color: {WHITE} !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: #555555 !important;
        -webkit-text-fill-color: #555555 !important;
        opacity: 1 !important;
    }}

    [data-testid="stChatInput"] button {{
        color: {BLACK} !important;
    }}

    .stSelectbox div[data-baseweb="select"] {{
        color: {BLACK} !important;
    }}

    /* Content cards */
    .study-card {{
        background-color: {WHITE};
        color: {BLACK};
        padding: 24px;
        border-radius: 16px;
        margin: 12px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }}

    .study-card h3 {{
        color: {GREEN} !important;
    }}

    .study-card p {{
        color: {BLACK} !important;
    }}

    .hero {{
        text-align: center;
        padding: 22px 10px 14px 10px;
    }}

    .hero h1 {{
        font-size: 42px;
        color: {GOLD} !important;
    }}

    .hero p {{
        color: {WHITE};
        font-size: 17px;
    }}

    .stAlert p {{
        color: inherit !important;
    }}

    hr {{
        border-color: rgba(255,255,255,0.3);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- SESSION STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "summary_result" not in st.session_state:
    st.session_state.summary_result = ""

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = ""

# ---------- GEMINI CLIENT ----------
from google.genai import types

def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        return genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30000
            )
        )
    except Exception as error:
        print(f"Gemini client error: {error}")
        return None
def ask_gemini(prompt):
    client = get_gemini_client()

       if client is None:
        return None

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        answer = response.text

        if answer and answer.strip():
            return answer.strip()

        print("Gemini returned an empty response.")
        return None

    except Exception as error:
        print(f"Gemini API error: {error}")
        return None
# ---------- SIDEBAR ----------
with st.sidebar:
    st.image(LOGO_URL, width=170)

    st.markdown(
        f"<h2 style='color:{GOLD};'>StudyMate AI</h2>",
        unsafe_allow_html=True
    )

    st.caption("Your personal AI study companion")
    st.divider()

    if st.button("🏠 Home", key="nav_home"):
        st.session_state.page = "Home"
        st.rerun()

    if st.button("📚 Study Chat", key="nav_chat"):
        st.session_state.page = "Study Chat"
        st.rerun()

    if st.button("📝 Summarizer", key="nav_summary"):
        st.session_state.page = "Summarizer"
        st.rerun()

    if st.button("🧠 Quiz Studio", key="nav_quiz"):
        st.session_state.page = "Quiz Studio"
        st.rerun()

    st.divider()

    st.markdown(
        f"<p style='color:{GOLD};font-weight:bold;'>"
        "TREE HOUSE HIGH SCHOOL</p>",
        unsafe_allow_html=True
    )

    st.caption("Learn smarter. Grow stronger.")


# ---------- HOME DASHBOARD ----------
if st.session_state.page == "Home":

    st.markdown(
        f"""
        <div class="hero">
            <img src="{LOGO_URL}" width="125">
            <h1>Welcome to StudyMate AI</h1>
            <p>Your learning journey starts here.</p>
            <p>Ask questions, simplify your notes, and test your knowledge.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        "<h2 style='text-align:center;'>Your Study Tools</h2>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="study-card">
            <h3>📚 Study Chat</h3>
            <p>Ask questions and understand your subjects.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open Study Chat", key="open_chat"):
            st.session_state.page = "Study Chat"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="study-card">
            <h3>📝 Summarizer</h3>
            <p>Turn lengthy notes into simple summaries.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open Summarizer", key="open_summary"):
            st.session_state.page = "Summarizer"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="study-card">
            <h3>🧠 Quiz Studio</h3>
            <p>Generate quizzes to test your knowledge.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open Quiz Studio", key="open_quiz"):
            st.session_state.page = "Quiz Studio"
            st.rerun()

    # ---------- CO-FOUNDERS ----------
    st.divider()

    st.markdown("""
    <div style="text-align:center;padding:25px 0 20px;">
        <h1 style="color:#FFD700 !important;">
            Meet Our Co-Founders
        </h1>
        <p style="color:white !important;font-size:17px;">
            The minds behind StudyMate AI
        </p>
    </div>
    """, unsafe_allow_html=True)

    founder1, founder2, founder3 = st.columns(3, gap="medium")

    founders = [
        (founder1, "Arjun Panchal"),
        (founder2, "Swwara Acharya"),
        (founder3, "Tanbi Mondal"),
    ]

    for column, name in founders:
        with column:
            st.markdown(
                f"""
                <div style="
                    background:#102F20;
                    border:2px solid #FFD700;
                    border-radius:16px;
                    padding:25px 8px;
                    text-align:center;
                    min-height:125px;
                ">
                    <div style="font-size:35px;">👑</div>
                    <h3 style="color:#FFD700 !important;
                               font-size:18px;">
                        {escape(name)}
                    </h3>
                    <p style="color:white !important;font-size:14px;">
                        Co-Founder
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("""
    <div style="text-align:center;padding:30px 0 10px;">
        <p style="color:#FFD700 !important;">
            © 2026 StudyMate AI | Built for students 💚
        </p>
        <p style="color:white !important;">
            Tree House High School
        </p>
    </div>
    """, unsafe_allow_html=True)



# ---------- STUDY CHAT ----------
elif st.session_state.page == "Study Chat":

    st.title("📚 Open Study Chat")
    st.write("Ask a question about any school subject.")

    subject = st.selectbox(
        "Choose your subject",
        [
            "General",
            "Mathematics",
            "Science",
            "Social Science",
            "English",
            "Computer Science"
        ]
    )

    # Display saved messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask your study question...")

    if question:
        # Save the question
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history_text = "\n".join(
                    f'{m["role"]}: {m["content"]}'
                    for m in st.session_state.chat_history[-10:]
                )

                answer = ask_gemini(
                    f"You are a friendly school tutor. "
                    f"The subject is {subject}. "
                    f"Explain concepts clearly at a school-student level. "
                    f"Show working for maths problems when useful.\n\n"
                    f"Conversation:\n{history_text}"
                )

            if answer:
                st.markdown(answer)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })
            else:
                st.warning(
                    "StudyMate couldn't get an answer this time. "
                    "Please try again. If the problem continues, "
                    "check the app logs."
                )

    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()
# ---------- SUMMARIZER ----------
elif st.session_state.page == "Summarizer":

    st.title("📝 Open Summarizer")
    st.write("Make your study notes easier to revise.")

    notes = st.text_area(
        "Paste your notes or chapter here",
        height=250,
        placeholder="Paste your text here..."
    )

    summary_style = st.selectbox(
        "Choose summary style",
        [
            "Simple and easy to understand",
            "Short revision notes",
            "Detailed summary",
            "Important points and definitions",
            "Exam-oriented notes"
        ]
    )

    if st.button("Generate Summary"):
        if not notes.strip():
            st.warning("Please enter some notes first.")
        else:
            with st.spinner("Summarizing your notes..."):
                result = ask_gemini(
                    f"Summarize these study notes in the following style: "
                    f"{summary_style}. Preserve important facts, definitions, "
                    f"formulas and key concepts. Do not invent information.\n\n"
                    f"NOTES:\n{notes}"
                )

                if result:
                    st.session_state.summary_result = result

    if st.session_state.summary_result:
        st.markdown("### Your Summary")
        st.markdown(
            f'<div class="study-card">'
            f'{escape(st.session_state.summary_result)}</div>',
            unsafe_allow_html=True
        )

        st.download_button(
            "Download Summary",
            data=st.session_state.summary_result,
            file_name="studymate_summary.txt",
            mime="text/plain"
        )


# ---------- QUIZ STUDIO ----------
elif st.session_state.page == "Quiz Studio":

    st.title("🧠 Open Quiz Studio")
    st.write("Create a practice quiz for your next test.")

    topic = st.text_input(
        "Enter your subject or topic",
        placeholder="e.g. Arithmetic Progressions"
    )

    difficulty = st.selectbox(
        "Choose difficulty",
        ["Easy", "Medium", "Hard"]
    )

    number_of_questions = st.slider(
        "Number of questions",
        min_value=5,
        max_value=20,
        value=10
    )

    quiz_type = st.selectbox(
        "Question type",
        [
            "Multiple-choice questions",
            "Short-answer questions",
            "Mixed questions"
        ]
    )

    if st.button("Generate Quiz"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Creating your quiz..."):
                result = ask_gemini(
                    f"Create a school-level practice quiz on {topic}. "
                    f"Difficulty: {difficulty}. "
                    f"Number of questions: {number_of_questions}. "
                    f"Question format: {quiz_type}. "
                    f"Number every question. For MCQs, provide four options. "
                    f"Put the answer key in a separate section at the end. "
                    f"Include explanations for the answers. "
                    f"Clearly label the answer key so students can avoid "
                    f"reading it until they finish."
                )

                if result:
                    st.session_state.quiz_result = result

    if st.session_state.quiz_result:
        st.markdown("### Your Practice Quiz")
        st.markdown(st.session_state.quiz_result)

        st.download_button(
            "Download Quiz",
            data=st.session_state.quiz_result,
            file_name="studymate_quiz.txt",
            mime="text/plain"
        )
