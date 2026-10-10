
import streamlit as st
from google import genai

# ---------------- APP CONFIG ----------------
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 StudyMate AI")
st.subheader("Your personal study companion")
st.write("Learn smarter. Revise faster. Do your best!")

# ---------------- GEMINI CONNECTION ----------------
def ask_ai(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        raise RuntimeError(
            "Gemini API key is not configured yet. "
            "Add GEMINI_API_KEY in Streamlit Secrets."
        )

    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "system_instruction": (
                "You are StudyMate AI, a helpful school tutor. "
                "Explain concepts clearly at Class 10 CBSE level. "
                "Be accurate, use examples, show working for maths, "
                "and admit uncertainty when needed."
            )
        },
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response. Please try again."
        )

    return response.text


# ---------------- SIDEBAR ----------------
tool = st.sidebar.selectbox(
    "Choose your study tool",
    ["Study Chat", "Summarizer", "Quiz Maker"],
)

st.sidebar.caption("StudyMate AI | Powered by Gemini")


# ---------------- STUDY CHAT ----------------
if tool == "Study Chat":
    st.header("💬 Study Chat")
    question = st.text_input("Ask any school question")

    if st.button("Get Answer"):
        if question.strip():
            with st.spinner("StudyMate is thinking..."):
                try:
                    st.markdown(ask_ai(question))
                except Exception:
                    st.error(
                        "Gemini couldn't answer right now. "
                        "Check your Streamlit Secrets and API key, "
                        "then try again."
                    )
        else:
            st.warning("Please type a question first.")


# ---------------- SUMMARIZER ----------------
elif tool == "Summarizer":
    st.header("📝 Text Summarizer")
    notes = st.text_area("Paste your study notes here")

    style = st.selectbox(
        "Summary style",
        [
            "Concise revision points",
            "Important definitions",
            "Exam-focused summary",
        ],
    )

    if st.button("Summarize"):
        if notes.strip():
            prompt = (
                f"Create {style.lower()} for a Class 10 CBSE student. "
                "Use clear headings and bullet points. Preserve "
                "important facts and do not invent information.\n\n"
                f"{notes}"
            )

            with st.spinner("Summarizing your notes..."):
                try:
                    st.markdown(ask_ai(prompt))
                except Exception:
                    st.error(
                        "Gemini couldn't summarize the notes. "
                        "Check your API configuration and try again."
                    )
        else:
            st.warning("Please paste some notes first.")


# ---------------- QUIZ MAKER ----------------
elif tool == "Quiz Maker":
    st.header("🧠 Quiz Maker")
    topic = st.text_input("Enter a topic")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
    )

    if st.button("Create Quiz"):
        if topic.strip():
            prompt = (
                f"Create exactly 5 {difficulty.lower()} difficulty "
                f"quiz questions about {topic} for a Class 10 CBSE "
                "student. Use multiple-choice questions with four "
                "options each. Clearly identify the correct answer "
                "and provide a brief explanation after each question. "
                "Use accurate educational information."
            )

            with st.spinner("Creating your quiz..."):
                try:
                    st.markdown(ask_ai(prompt))
                except Exception:
                    st.error(
                        "Gemini couldn't create the quiz. "
                        "Check your API configuration and try again."
                    )
        else:
            st.warning("Please enter a topic.")
