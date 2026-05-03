import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.llm_insights import chat_with_analyst

st.set_page_config(
    page_title="PRISM — AI Analyst",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Cinema Analyst")
st.caption(
    "Ask anything about Indian cinema — "
    "PRISM answers from real data, not guesswork"
)

st.markdown("---")


st.markdown("**Try asking:**")
col1, col2, col3 = st.columns(3)

questions = [
    "Which genre rates highest?",
    "Tell me about Malayalam hidden gems",
    "Has Indian cinema gotten shorter?",
    "What is the highest rated film?",
    "Why does popular not equal good?",
    "Which decade was most productive?"
]

for i, (col, q) in enumerate(
    zip([col1, col2, col3] * 2, questions)
):
    with col:
        if st.button(q, key=f"q_{i}"):
            st.session_state.chat_input = q

st.markdown("---")


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "llm_history" not in st.session_state:
    st.session_state.llm_history = []

# Display existing chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat Input ────────────────────────────────────
user_input = st.chat_input(
    "Ask me anything about Indian cinema...",
)


if st.session_state.get("chat_input"):
    user_input = st.session_state.chat_input
    st.session_state.chat_input = None

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Get LLM response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = chat_with_analyst(
                user_input,
                st.session_state.llm_history
            )

        answer = result["answer"]
        st.session_state.llm_history = result["history"]

        st.markdown(answer)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })


if st.session_state.chat_history:
    if st.button("🗑️ Clear conversation"):
        st.session_state.chat_history = []
        st.session_state.llm_history = []
        st.rerun()