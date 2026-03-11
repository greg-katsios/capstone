"""
Echo Chat App — No API Key Required
======================================
Use this version to test the chat interface without an LLM.
The assistant echoes back what you type.

Run with:
    streamlit run app_echo.py
"""

import streamlit as st

# ── Page config ──────────────────────────────────────────────────

st.set_page_config(page_title="Echo Chat", page_icon="🔁")
st.title("🔁 Echo Chat")
st.write("A test chat interface — the assistant echoes your messages.")

# ── Sidebar ──────────────────────────────────────────────────────

with st.sidebar:
    st.header("Settings")
    st.info("This is the echo version. No API key needed.")
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

if prompt := st.chat_input("Type something..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Echo it back as assistant
    reply = f"You said: {prompt}"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
