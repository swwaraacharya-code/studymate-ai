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
# LOGO HTML HELPER
# =========================================================

BOOK_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
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
  <path d="M60 15 L63 23 L71 26 L63 29 L60 37 L57 29 L49 26 L57 23 Z"
        fill="#D8BB7A"/>
</svg>
"""

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
            '<div style="background:linear-gradient(135deg,#102A22,#174B38);'
            'border:1px solid #D8BB7A;border-radius:16px;padding:24px;'
            'text-align:center;">'
            '<div style="font-size:42px;">🎓</div>'
            '<h2 style="color:#D8BB7A;">40 minutes. Great effort!</h2>'
            '<p style="color:#E5F1EA;">You have completed a focus session.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.write("Take a moment to rest your eyes and stretch.")

        if st.button("✅ Continue studying", use_container_width=True):
            st.session_state.focus_reminder_pending = False
            st.session_state.focus_start_time = time.time()
            st.rerun()

        if st.button("☕ Take a short break", use_container_width=True):
            st.session_state.focus_reminder_pending = False
            st.session_state.focus_start_time = None
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
