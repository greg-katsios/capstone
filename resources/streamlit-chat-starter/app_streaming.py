"""
Streaming Chat App — Stretch Goal
====================================
Shows LLM responses token-by-token.

Run with:
    streamlit run app_streaming.py

Make sure Ollama is running first.
"""

import streamlit as st
from ollama import chat

# ── Page config ──────────────────────────────────────────────────

st.set_page_config(page_title="Streaming Chat", page_icon="⚡")
st.title("⚡ Streaming Chat App")
st.write("Responses appear token-by-token as they're generated.")

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

# ── Stream helper ────────────────────────────────────────────────

def stream_response(model, system, temperature, messages):
    """Yield text chunks from the Ollama streaming API."""
    full_messages = [{"role": "system", "content": system}] + messages
    stream = chat(
        model=model,
        messages=full_messages,
        options={"temperature": temperature},
        stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]

# ── Handle new user input ────────────────────────────────────────

if prompt := st.chat_input("Ask something..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Stream assistant response
    with st.chat_message("assistant"):
        reply = st.write_stream(
            stream_response(model, system_prompt, temperature, st.session_state.messages)
        )

    # Save the complete response
    st.session_state.messages.append({"role": "assistant", "content": reply})
