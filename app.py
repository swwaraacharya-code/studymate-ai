import streamlit as st
import ollama

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 StudyMate AI")
st.subheader("Your personal study companion")
st.write("Learn smarter. Revise faster. Do your best!")

tool = st.sidebar.selectbox(
    "Choose your study tool",
    ["Study Chat", "Summarizer", "Quiz Maker"]
)

def ask_ai(prompt):
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are StudyMate AI, a helpful school tutor. "
                    "Explain concepts clearly at Class 10 CBSE level. "
                    "Be accurate, use examples, and admit uncertainty "
                    "when needed."
                )
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]

if tool == "Study Chat":
    st.header("💬 Study Chat")
    question = st.text_input("Ask any school question")

    if st.button("Get Answer"):
        if question.strip():
            with st.spinner("StudyMate is thinking..."):
                try:
                    st.markdown(ask_ai(question))
                except Exception as e:
                    st.error(
                        "Could not connect to Ollama. "
                        "Make sure Ollama is running."
                    )
                    st.caption(str(e))
        else:
            st.warning("Please type a question first.")

elif tool == "Summarizer":
    st.header("📝 Text Summarizer")
    text = st.text_area("Paste your study notes here")

    if st.button("Summarize"):
        if text.strip():
            with st.spinner("Summarizing your notes..."):
                try:
                    st.markdown(
                        ask_ai(
                            "Summarize these notes into concise "
                            "Class 10 revision points:\n\n" + text
                        )
                    )
                except Exception as e:
                    st.error("Could not connect to Ollama.")
                    st.caption(str(e))
        else:
            st.warning("Please paste some notes first.")

elif tool == "Quiz Maker":
    st.header("🧠 Quiz Maker")
    topic = st.text_input("Enter a topic")
    difficulty = st.selectbox(
        "Difficulty", ["Easy", "Medium", "Hard"]
    )

    if st.button("Create Quiz"):
        if topic.strip():
            with st.spinner("Creating your quiz..."):
                try:
                    st.markdown(
                        ask_ai(
                            f"Create 5 {difficulty.lower()} difficulty "
                            f"Class 10 quiz questions on {topic}. "
                            "Include multiple-choice options, then give "
                            "an answer key with brief explanations "
                            "at the end."
                        )
                    )
                except Exception as e:
                    st.error("Could not connect to Ollama.")
                    st.caption(str(e))
        else:
            st.warning("Please enter a topic.")

st.sidebar.caption("StudyMate AI | Powered by Ollama")
