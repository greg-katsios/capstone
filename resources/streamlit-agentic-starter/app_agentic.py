import yaml
import streamlit as st
from pathlib import Path
from datetime import datetime
from ollama import chat
from tools import TOOL_FUNCTIONS, get_tools_for_persona

# ── Persona loader ──────────────────────────────────────────────

def load_personas(directory: str = "personas") -> dict:
    """Load all persona YAML files from a directory."""
    personas = {}
    persona_dir = Path(directory)
    for filepath in sorted(persona_dir.glob("*.yaml")):
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        persona_id = filepath.stem
        personas[persona_id] = data
    return personas

# ── Page config ─────────────────────────────────────────────────

st.set_page_config(page_title="Agentic Chat", page_icon="🤖")
st.title("🤖 Agentic Persona Chat")

# ── Initialize state ────────────────────────────────────────────

if "personas" not in st.session_state:
    st.session_state.personas = load_personas()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_persona" not in st.session_state:
    st.session_state.active_persona = None

if "memory" not in st.session_state:
    st.session_state.memory = {}

if "tool_log" not in st.session_state:
    st.session_state.tool_log = []

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

    model = st.text_input("Model", value="llama3.1")

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

    # ── Tools ───────────────────────────────────────────────────
    st.header("Tools")

    tools_enabled = st.checkbox("Enable tools", value=True)

    persona_tools = get_tools_for_persona(persona) if tools_enabled else []
    tool_names = [fn.__name__ for fn in persona_tools]
    if tool_names:
        st.caption(f"Available: {', '.join(tool_names)}")
    else:
        st.caption("No tools enabled")

    st.divider()

    # ── Execution Log ───────────────────────────────────────────
    st.header("Execution Log")

    if st.session_state.tool_log:
        for entry in reversed(st.session_state.tool_log):
            with st.expander(f"{entry['tool']} — {entry['timestamp']}", expanded=False):
                st.markdown(f"**Persona:** {entry['persona']}")
                st.markdown("**Input:**")
                st.json(entry["args"])
                st.markdown("**Output:**")
                st.code(entry["result"], language=None)
    else:
        st.caption("No tool calls yet")

    st.divider()

    # ── Actions ─────────────────────────────────────────────────
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory = {}
        st.session_state.tool_log = []
        st.rerun()

# ── Handle persona switch ───────────────────────────────────────

if st.session_state.active_persona != persona_id:
    st.session_state.active_persona = persona_id
    st.session_state.messages = []
    st.session_state.memory = {}
    st.session_state.tool_log = []

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
        # Re-render tool call expanders for assistant messages
        for tc in msg.get("tool_calls", []):
            with st.expander(f"Tool: {tc['name']}", expanded=False):
                st.json(tc["args"])
                st.success(tc["result"])
        st.write(msg["content"])

# ── Build messages helper ───────────────────────────────────────

def build_messages(system_prompt, chat_history):
    """Prepend the system prompt to the chat history."""
    system_msg = {"role": "system", "content": system_prompt}
    return [system_msg] + [
        {"role": m["role"], "content": m["content"]}
        for m in chat_history
    ]

# ── Execute a tool call ─────────────────────────────────────────

def run_tool_call(tool_call):
    """Look up and execute a tool function. Returns the result string."""
    name = tool_call.function.name
    args = tool_call.function.arguments
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return f"Unknown tool: {name}"
    try:
        result = fn(**args)
    except Exception as e:
        result = f"Error: {e}"

    st.session_state.tool_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "persona": persona["name"],
        "tool": name,
        "args": dict(args),
        "result": result,
    })
    return result

# ── Handle new user input ───────────────────────────────────────

if prompt := st.chat_input("Ask something..."):
    # 1. Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Call the LLM with tools
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages = build_messages(system_prompt, st.session_state.messages)
            response = chat(
                model=model,
                messages=messages,
                tools=persona_tools if persona_tools else None,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": num_predict,
                },
            )

        # 3. Handle tool calls if present
        tool_results_display = []

        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                result = run_tool_call(tool_call)
                tool_results_display.append({
                    "name": tool_call.function.name,
                    "args": dict(tool_call.function.arguments),
                    "result": result,
                })
                with st.expander(f"Tool: {tool_call.function.name}", expanded=True):
                    st.json(dict(tool_call.function.arguments))
                    st.success(result)

            # Build follow-up messages with tool results
            messages.append(response.message)
            for i, tool_call in enumerate(response.message.tool_calls):
                messages.append({
                    "role": "tool",
                    "content": tool_results_display[i]["result"],
                })

            # Second LLM call with tool results
            with st.spinner("Thinking with tool results..."):
                final_response = chat(
                    model=model,
                    messages=messages,
                    options={
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": num_predict,
                    },
                )
                reply = final_response.message.content or ""
        else:
            reply = response.message.content or ""

        # 4. Display and save the response
        st.write(reply)
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "tool_calls": tool_results_display,
        })
