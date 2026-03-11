"""
Streamlit Chat App — Starter Code
===================================
A minimal chat interface connected to an LLM.

Run with:
    streamlit run app.py

Make sure Ollama is running first.
"""

import streamlit as st
from ollama import chat

# ── Page config ──────────────────────────────────────────────────

st.set_page_config(page_title="Chat App", page_icon="💬")
st.title("💬 My Chat App")
st.write("A simple chatbot powered by Ollama.")

# ── Sidebar settings ─────────────────────────────────────────────

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Model", value="llama3.2")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, step=0.1)
    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful assistant. Be concise.",
        height=100,
    )

    st.divider()
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ── Initialize state ─────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display conversation history ─────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Handle new user input ────────────────────────────────────────

if prompt := st.chat_input("Ask something..."):
    # 1. Append user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Display user message immediately
    with st.chat_message("user"):
        st.write(prompt)

    # 3. Call the LLM
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Build messages list with system prompt
            messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            response = chat(
                model=model,
                messages=messages,
                options={"temperature": temperature},
            )
            reply = response["message"]["content"]

        # 4. Display and save the response
        st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
