"""
Research-Grade Persona Chat with Telemetry

Extends the agentic chat interface with:
  - Structured JSON logging (Python logging module)
  - SQLite telemetry database (sessions, messages, tool_calls)
  - Response time measurement on every LLM call
  - User feedback (thumbs up / thumbs down)
  - Session management with replay and JSON export
  - Privacy controls (opt-in telemetry, PII anonymization)

Run:
    streamlit run app_telemetry.py --server.address localhost
"""

import time
import yaml
import streamlit as st
from pathlib import Path
from datetime import datetime
from ollama import chat
from tools import TOOL_FUNCTIONS, get_tools_for_persona
from telemetry import TelemetryLogger

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

st.set_page_config(page_title="Telemetry Chat", page_icon="📊")
st.title("📊 Research-Grade Persona Chat")

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

# ── Telemetry state ─────────────────────────────────────────────

if "telemetry" not in st.session_state:
    st.session_state.telemetry = TelemetryLogger()

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "replay_session_id" not in st.session_state:
    st.session_state.replay_session_id = None

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

    # ── Telemetry Settings ──────────────────────────────────────
    st.header("Telemetry")

    telemetry_enabled = st.checkbox("Enable telemetry", value=True)
    anonymize = st.checkbox("Anonymize inputs", value=False)

    if telemetry_enabled:
        st.caption("Logging to logs/telemetry.log + telemetry.db")
    else:
        st.caption("Telemetry disabled — nothing is recorded")

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
                if "duration_ms" in entry:
                    st.caption(f"Duration: {entry['duration_ms']:.1f} ms")
    else:
        st.caption("No tool calls yet")

    st.divider()

    # ── Session History ─────────────────────────────────────────
    st.header("Session History")

    tl = st.session_state.telemetry
    sessions = tl.get_sessions()

    if sessions:
        for sess in sessions[:10]:
            sid = sess["session_id"]
            label = f"{sess['persona_name']} — {sess['message_count']} msgs"
            with st.expander(label, expanded=False):
                st.caption(f"ID: {sid}")
                st.caption(f"Started: {sess['started_at'][:19]}")
                if sess["ended_at"]:
                    st.caption(f"Ended: {sess['ended_at'][:19]}")
                else:
                    st.caption("Status: active")

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Replay", key=f"replay_{sid}"):
                        st.session_state.replay_session_id = sid
                        st.rerun()
                with col_b:
                    export_json = tl.export_session(sid)
                    st.download_button(
                        "Export",
                        data=export_json,
                        file_name=f"session_{sid}.json",
                        mime="application/json",
                        key=f"export_{sid}",
                    )
    else:
        st.caption("No sessions recorded yet")

    st.divider()

    # ── Actions ─────────────────────────────────────────────────
    if st.button("Clear conversation", use_container_width=True):
        if st.session_state.session_id and telemetry_enabled:
            tl.end_session(st.session_state.session_id)
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.memory = {}
        st.session_state.tool_log = []
        st.rerun()

# ── Handle persona switch ───────────────────────────────────────

if st.session_state.active_persona != persona_id:
    # End previous telemetry session
    if st.session_state.session_id and telemetry_enabled:
        tl.end_session(st.session_state.session_id)

    st.session_state.active_persona = persona_id
    st.session_state.messages = []
    st.session_state.memory = {}
    st.session_state.tool_log = []

    # Start new telemetry session
    if telemetry_enabled:
        st.session_state.session_id = tl.start_session(
            persona_name=persona["name"],
            model=model,
        )
    else:
        st.session_state.session_id = None

    greeting = persona.get("greeting")
    if greeting:
        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )
    st.rerun()

# Auto-start a telemetry session if we have a persona but no session
if telemetry_enabled and st.session_state.session_id is None and st.session_state.active_persona:
    st.session_state.session_id = tl.start_session(
        persona_name=persona["name"],
        model=model,
    )

# ── Session replay mode ────────────────────────────────────────

if st.session_state.replay_session_id:
    replay_sid = st.session_state.replay_session_id
    replay_msgs = tl.get_session_messages(replay_sid)
    replay_tools = tl.get_session_tool_calls(replay_sid)

    st.info(f"Replaying session **{replay_sid}** ({len(replay_msgs)} messages)")

    if st.button("Back to chat"):
        st.session_state.replay_session_id = None
        st.rerun()

    for msg in replay_msgs:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["response_time_ms"] is not None:
                st.caption(f"Response time: {msg['response_time_ms']:.0f} ms")
            if msg["feedback"]:
                st.caption(f"Feedback: {msg['feedback']}")

    if replay_tools:
        st.subheader("Tool Calls in This Session")
        for tc in replay_tools:
            with st.expander(f"{tc['tool_name']} — {tc['timestamp'][:19]}"):
                st.json(tc["args_json"])
                st.code(tc["result"], language=None)
                if tc["duration_ms"] is not None:
                    st.caption(f"Duration: {tc['duration_ms']:.1f} ms")

    st.stop()

# ── Subtitle ────────────────────────────────────────────────────

st.write(f"Chatting with **{persona.get('avatar', '')} {persona['name']}**")

# ── Display conversation history ────────────────────────────────

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        for tc in msg.get("tool_calls", []):
            with st.expander(f"Tool: {tc['name']}", expanded=False):
                st.json(tc["args"])
                st.success(tc["result"])
        st.write(msg["content"])

        # Response time display
        if msg.get("response_time_ms") is not None:
            st.caption(f"Response time: {msg['response_time_ms']:.0f} ms")

        # Feedback buttons for assistant messages
        if msg["role"] == "assistant":
            existing_fb = msg.get("feedback")
            if existing_fb:
                st.caption(f"Feedback: {existing_fb}")
            else:
                col_fb1, col_fb2, col_fb_spacer = st.columns([1, 1, 10])
                with col_fb1:
                    if st.button("👍", key=f"up_{i}"):
                        msg["feedback"] = "thumbs_up"
                        if telemetry_enabled and st.session_state.session_id:
                            tl.log_feedback(
                                st.session_state.session_id, i, "thumbs_up",
                            )
                        st.rerun()
                with col_fb2:
                    if st.button("👎", key=f"down_{i}"):
                        msg["feedback"] = "thumbs_down"
                        if telemetry_enabled and st.session_state.session_id:
                            tl.log_feedback(
                                st.session_state.session_id, i, "thumbs_down",
                            )
                        st.rerun()

# ── Build messages helper ───────────────────────────────────────

def build_messages(sys_prompt, chat_history):
    """Prepend the system prompt to the chat history."""
    system_msg = {"role": "system", "content": sys_prompt}
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

    tool_start = time.time()
    try:
        result = fn(**args)
    except Exception as e:
        result = f"Error: {e}"
    tool_duration_ms = (time.time() - tool_start) * 1000

    st.session_state.tool_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "persona": persona["name"],
        "tool": name,
        "args": dict(args),
        "result": result,
        "duration_ms": tool_duration_ms,
    })

    if telemetry_enabled and st.session_state.session_id:
        tl.log_tool_call(
            st.session_state.session_id,
            tool_name=name,
            args=dict(args),
            result=result,
            duration_ms=tool_duration_ms,
            persona_name=persona["name"],
        )

    return result

# ── Handle new user input ───────────────────────────────────────

if prompt := st.chat_input("Ask something..."):
    # 1. Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Log user message
    if telemetry_enabled and st.session_state.session_id:
        tl.log_message(
            st.session_state.session_id,
            role="user",
            content=prompt,
            anonymize=anonymize,
        )

    # 2. Call the LLM with tools (timed)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages = build_messages(system_prompt, st.session_state.messages)

            start_time = time.time()
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
            first_call_ms = (time.time() - start_time) * 1000

        # 3. Handle tool calls if present
        tool_results_display = []
        total_response_ms = first_call_ms

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
            for idx, tool_call in enumerate(response.message.tool_calls):
                messages.append({
                    "role": "tool",
                    "content": tool_results_display[idx]["result"],
                })

            # Second LLM call with tool results (timed)
            with st.spinner("Thinking with tool results..."):
                second_start = time.time()
                final_response = chat(
                    model=model,
                    messages=messages,
                    options={
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": num_predict,
                    },
                )
                second_call_ms = (time.time() - second_start) * 1000
                total_response_ms = first_call_ms + second_call_ms
                reply = final_response.message.content or ""
        else:
            reply = response.message.content or ""

        # 4. Display the response with timing
        st.write(reply)
        st.caption(f"Response time: {total_response_ms:.0f} ms")

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "tool_calls": tool_results_display,
            "response_time_ms": total_response_ms,
        })

        # Log assistant message
        if telemetry_enabled and st.session_state.session_id:
            tl.log_message(
                st.session_state.session_id,
                role="assistant",
                content=reply,
                response_time_ms=total_response_ms,
                anonymize=anonymize,
            )
