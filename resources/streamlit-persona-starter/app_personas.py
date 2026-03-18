import yaml
import streamlit as st
from pathlib import Path
from ollama import chat

# ── Persona loader ──────────────────────────────────────────────

def load_personas(directory: str = "personas") -> dict:
    """Load all persona YAML files from a directory."""
    personas = {}
    persona_dir = Path(directory)
    for filepath in sorted(persona_dir.glob("*.yaml")):
        with open(filepath, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        persona_id = filepath.stem  # e.g. "analyst"
        personas[persona_id] = data
    return personas

# ── Page config ─────────────────────────────────────────────────

st.set_page_config(page_title="Persona Chat", page_icon="🎭")
st.title("🎭 Persona Chat")

# ── Initialize state ────────────────────────────────────────────

if "personas" not in st.session_state:
    st.session_state.personas = load_personas()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_persona" not in st.session_state:
    st.session_state.active_persona = None

# ── Sidebar ─────────────────────────────────────────────────────

with st.sidebar:

    # ── Persona Selection ────────────────────────────────────────
    st.header("Persona")

    persona_ids = list(st.session_state.personas.keys())
    personas = st.session_state.personas

    persona_id = st.selectbox(
        "Active persona",
        options=persona_ids,
        format_func=lambda pid: f"{personas[pid].get('avatar', '')} {personas[pid]['name']}",
    )

    persona = personas[persona_id]
    st.caption(persona["bio"])

    with st.expander("View Profile"):
        st.markdown(
            f"**Traits:** {', '.join(persona['traits'])}  \n"
            f"**Expertise:** {', '.join(persona['expertise'])}  \n"
            f"**Tone:** {persona['style']['tone']}"
        )

    st.divider()

    # ── LLM Settings ────────────────────────────────────────────
    st.header("LLM Settings")

    model = st.text_input("Model", value="llama3.2")

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "Temperature",
            0.0, 1.0,
            value=persona.get("temperature", 0.7),
            step=0.1,
        )
    with col2:
        top_p = st.slider(
            "Top P",
            0.0, 1.0,
            value=persona.get("top_p", 0.9),
            step=0.05,
        )

    num_predict = st.number_input(
        "Max tokens",
        min_value=64,
        max_value=4096,
        value=persona.get("num_predict", 1024),
        step=64,
    )

    with st.expander("System Prompt"):
        system_prompt = st.text_area(
            "Edit the prompt sent to the LLM",
            value=persona["system_prompt"],
            height=150,
            label_visibility="collapsed",
        )

    st.divider()

    # ── Actions ─────────────────────────────────────────────────
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Handle persona switch ───────────────────────────────────────

if st.session_state.active_persona != persona_id:
    st.session_state.active_persona = persona_id
    st.session_state.messages = []

    # Inject greeting message if the persona has one
    greeting = persona.get("greeting")
    if greeting:
        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )
    st.rerun()

# ── Subtitle ────────────────────────────────────────────────────

st.write(f"Chatting with **{persona.get('avatar', '')} {persona['name']}**")

# ── Display conversation history ────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Build messages helper ───────────────────────────────────────

def build_messages(system_prompt, chat_history):
    """Prepend the system prompt to the chat history."""
    system_msg = {"role": "system", "content": system_prompt}
    return [system_msg] + chat_history

# ── Handle new user input ───────────────────────────────────────

if prompt := st.chat_input("Ask something..."):
    # 1. Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Call the LLM using sidebar settings (persona defaults + user overrides)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages = build_messages(system_prompt, st.session_state.messages)
            response = chat(
                model=model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": num_predict,
                },
            )
            reply = response["message"]["content"]

        # 3. Display and save the response
        st.write(reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
