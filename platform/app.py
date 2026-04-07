import streamlit as st
import pandas as pd
import numpy as np
import base64
from pathlib import Path
from ollama import chat

def set_image_as_background(image_path):
    image_file = Path(image_path)
    if not image_file.is_absolute():
        image_file = Path(__file__).parent / image_file

    if not image_file.exists():
        st.error(f"Background image not found: {image_file}")
        return

    encoded_image = base64.b64encode(image_file.read_bytes()).decode("utf-8")
    ext = image_file.suffix.lower().lstrip(".") or "png"
    if ext == "jpg":
        ext = "jpeg"

    st.markdown(
        f"""
        <style>
        .stApp,
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/{ext};base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        [data-testid="stHeader"],
        [data-testid="stToolbar"] {{
            background: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ── Page config ──────────────────────────────────────────────────

st.set_page_config(page_title="Persona Weave App", page_icon="💬")
st.title("Persona Weave App")
st.write("This is a Streamlit App that will house the Persona Weave interface.")

# st.navigation(pages, position="top")
set_image_as_background("assets/landing_page_background.png")

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