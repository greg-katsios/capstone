import streamlit as st
import base64
import json
import re
from pathlib import Path
from datetime import datetime
from ollama import chat

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(page_title="Persona Weave App", page_icon="💬", layout="wide")

# ── Background helper ────────────────────────────────────────────
def set_image_as_background(image_path):
    image_file = Path(image_path)
    if not image_file.is_absolute():
        image_file = Path(__file__).parent / image_file
    if not image_file.exists():
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
        unsafe_allow_html=True,
    )

set_image_as_background("assets/landing_page_background.png")

# ════════════════════════════════════════════════════════════════
#  TOOL DEFINITIONS  (schema sent to Ollama)
# ════════════════════════════════════════════════════════════════
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": (
                "Save an important fact about the user to long-term memory. "
                "Use this whenever the user shares their name, preferences, "
                "interests, or any detail worth remembering later."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Short label for the fact, e.g. 'name', 'favorite_color'",
                    },
                    "value": {
                        "type": "string",
                        "description": "The fact to remember",
                    },
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": (
                "Retrieve a previously saved fact about the user. "
                "Use this when the user asks what you remember, or when "
                "context from earlier conversations would improve your reply."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The label of the fact to look up",
                    }
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": (
                "Return the current local date and time. "
                "Use this when the user asks what time or date it is, "
                "or when a time-aware response would be helpful."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sentiment",
            "description": (
                "Analyze the emotional tone of the user's latest message. "
                "Returns a sentiment label (positive / neutral / negative) "
                "and a suggested empathy strategy. Use this when the user "
                "seems frustrated, sad, excited, or emotionally charged."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The user message to analyze",
                    }
                },
                "required": ["text"],
            },
        },
    },
]

# ════════════════════════════════════════════════════════════════
#  TOOL IMPLEMENTATIONS
# ════════════════════════════════════════════════════════════════
def normalize_to_string(value):
    """Convert tool argument values into a safe string."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for candidate_key in ["key", "value", "fact", "memory", "topic", "name"]:
            if candidate_key in value:
                return str(value[candidate_key]).strip()
        return json.dumps(value)
    if value is None:
        return ""
    return str(value).strip()


def save_memory(key, value) -> str:
    if "memory" not in st.session_state:
        st.session_state.memory = {}

    key = normalize_to_string(key).lower()
    value = normalize_to_string(value)

    if not key:
        return "Tool error: memory key was empty."

    st.session_state.memory[key] = value
    return f"Saved: {key} = {value}"


def recall_memory(key) -> str:
    memory = st.session_state.get("memory", {})

    key = normalize_to_string(key).lower()

    if not key:
        if memory:
            return "Known memory: " + ", ".join(f"{k}={v}" for k, v in memory.items())
        return "Memory is empty"

    val = memory.get(key)
    if val is not None:
        return f"Recalled: {key} = {val}"

    all_keys = list(memory.keys())
    if all_keys:
        return f"No memory for '{key}'. Known keys: {', '.join(all_keys)}"
    return "Memory is empty"


def get_current_time() -> str:
    now = datetime.now()
    return now.strftime("Today is %A, %B %d, %Y. The current time is %I:%M %p.")


def analyze_sentiment(text: str) -> str:
    text_lower = text.lower()
    negative_words = [
        "sad", "angry", "frustrated", "hate", "terrible", "awful",
        "horrible", "bad", "worst", "annoyed", "upset", "depressed",
        "stressed", "worried", "scared", "anxious",
    ]
    positive_words = [
        "happy", "great", "love", "awesome", "excellent", "amazing",
        "wonderful", "fantastic", "good", "excited", "thrilled", "glad",
        "thankful", "grateful", "brilliant",
    ]
    neg_count = sum(1 for w in negative_words if w in text_lower)
    pos_count = sum(1 for w in positive_words if w in text_lower)

    if neg_count > pos_count:
        sentiment = "negative"
        strategy = (
            "Acknowledge feelings first. Use empathetic, calm language. "
            "Offer support before solutions."
        )
    elif pos_count > neg_count:
        sentiment = "positive"
        strategy = (
            "Match the user's enthusiasm. Be warm and encouraging. "
            "Build on their positive energy."
        )
    else:
        sentiment = "neutral"
        strategy = "Keep a balanced, helpful tone. Focus on clarity and usefulness."

    return json.dumps({"sentiment": sentiment, "strategy": strategy})


# ════════════════════════════════════════════════════════════════
#  TOOL DISPATCHER
# ════════════════════════════════════════════════════════════════
TOOL_FN_MAP = {
    "save_memory": save_memory,
    "recall_memory": recall_memory,
    "get_current_time": get_current_time,
    "analyze_sentiment": analyze_sentiment,
}

TOOL_ICONS = {
    "save_memory": "🧠",
    "recall_memory": "🔍",
    "get_current_time": "🕒",
    "analyze_sentiment": "❤️",
}

TOOL_CATEGORY = {
    "save_memory": "Memory",
    "recall_memory": "Memory",
    "get_current_time": "Context",
    "analyze_sentiment": "Emotional",
}


def dispatch_tool(tool_name: str, tool_args: dict) -> str:
    fn = TOOL_FN_MAP.get(tool_name)
    if fn is None:
        return f"Unknown tool: {tool_name}"

    try:
        import inspect
        valid_params = inspect.signature(fn).parameters.keys()
        filtered_args = {k: v for k, v in tool_args.items() if k in valid_params}

        # debug
        print(f"[TOOL] {tool_name} raw_args={tool_args} filtered_args={filtered_args}")

        return fn(**filtered_args)
    except Exception as e:
        return f"Tool error: {e}"


# ════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ════════════════════════════════════════════════════════════════
for key, default in [
    ("messages", []),
    ("memory", {}),
    ("execution_logs", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("⚙️ Settings")
    model = st.text_input("Model", value="llama3.2")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, step=0.1)
    system_prompt = st.text_area(
        "System prompt",
        value=(
            "You are a helpful, empathetic assistant called Persona Weave. "
            "You have access to tools — use them autonomously whenever they "
            "would improve your response. Always save important user facts to "
            "memory and recall them when relevant."
        ),
        height=130,
    )
    st.divider()
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.session_state.execution_logs = []
        st.rerun()
    if st.button("🧹 Clear memory"):
        st.session_state.memory = {}
        st.rerun()

    # ── Memory viewer ────────────────────────────────────────────
    st.divider()
    st.subheader("🧠 Saved Memory")
    if st.session_state.memory:
        for k, v in st.session_state.memory.items():
            st.markdown(f"**{k}:** {v}")
    else:
        st.caption("Nothing saved yet.")

    # ── Execution logs ────────────────────────────────────────────
    st.divider()
    st.subheader("📋 Execution Logs")
    if st.session_state.execution_logs:
        for log in reversed(st.session_state.execution_logs[-30:]):
            st.markdown(log)
    else:
        st.caption("No tool calls yet.")


# ════════════════════════════════════════════════════════════════
#  MAIN CHAT UI
# ════════════════════════════════════════════════════════════════
st.title("💬 Persona Weave")
st.caption("Agentic chat with autonomous tool use")

# Replay chat history
for msg in st.session_state.messages:
    role = msg["role"]
    if role == "tool":
        continue  # tool results are shown inline via expanders
    with st.chat_message(role):
        # Render any tool call expanders stored in the message
        if "tool_calls_display" in msg:
            for tc in msg["tool_calls_display"]:
                icon = TOOL_ICONS.get(tc["name"], "🔧")
                category = TOOL_CATEGORY.get(tc["name"], "Tool")
                label = f"{icon} {category} · `{tc['name']}`"
                with st.expander(label, expanded=False):
                    st.json(tc["args"])
                    st.markdown("**Result:**")
                    st.code(tc["result"], language="text")
        if msg.get("content"):
            st.write(msg["content"])


# ════════════════════════════════════════════════════════════════
#  AGENTIC RESPONSE LOOP
# ════════════════════════════════════════════════════════════════
def run_agent(user_prompt: str, model: str, system: str, temperature: float):
    """
    Agentic loop:
    1. Call Ollama with tools.
    2. If the model requests tool calls, execute them and feed results back.
    3. Repeat until the model returns a plain text reply.
    Returns the final reply text and a list of tool call display dicts.
    """
    ollama_messages = [{"role": "system", "content": system}]
    # Convert stored messages (skip tool-result role, already embedded)
    for m in st.session_state.messages:
        if m["role"] in ("user", "assistant") and m.get("content"):
            ollama_messages.append({"role": m["role"], "content": m["content"]})
    ollama_messages.append({"role": "user", "content": user_prompt})

    tool_calls_display = []

    for _ in range(8):  # max agentic iterations
        response = chat(
            model=model,
            messages=ollama_messages,
            tools=TOOL_SCHEMAS,
            options={"temperature": temperature},
            stream=False,
        )
        assistant_msg = response["message"]

        # If no tool calls → final answer
        if not assistant_msg.get("tool_calls"):
            return assistant_msg.get("content", ""), tool_calls_display

        # Append the assistant's tool-call request to the conversation
        ollama_messages.append(assistant_msg)

        # Execute each tool call
        for tc in assistant_msg["tool_calls"]:
            fn_name = tc["function"]["name"]
            fn_args = tc["function"]["arguments"]
            if isinstance(fn_args, str):
                try:
                    fn_args = json.loads(fn_args)
                except json.JSONDecodeError:
                    fn_args = {}

            result = dispatch_tool(fn_name, fn_args)

            # Log to sidebar
            ts = datetime.now().strftime("%H:%M:%S")
            icon = TOOL_ICONS.get(fn_name, "🔧")
            category = TOOL_CATEGORY.get(fn_name, "Tool")
            st.session_state.execution_logs.append(
                f"`{ts}` {icon} **{category}** › `{fn_name}` → {result[:80]}"
            )

            # Store for expander display
            tool_calls_display.append(
                {"name": fn_name, "args": fn_args, "result": result}
            )

            # Feed tool result back
            ollama_messages.append(
                {
                    "role": "tool",
                    "content": result,
                }
            )

    return "I've finished processing but didn't produce a final reply.", tool_calls_display


# ════════════════════════════════════════════════════════════════
#  HANDLE USER INPUT
# ════════════════════════════════════════════════════════════════
if prompt := st.chat_input("Ask something..."):
    # Show user bubble
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                reply, tool_calls_display = run_agent(
                    prompt, model, system_prompt, temperature
                )

                # Render tool call expanders inline
                for tc in tool_calls_display:
                    icon = TOOL_ICONS.get(tc["name"], "🔧")
                    category = TOOL_CATEGORY.get(tc["name"], "Tool")
                    label = f"{icon} {category} · `{tc['name']}`"
                    with st.expander(label, expanded=True):
                        st.json(tc["args"])
                        st.markdown("**Result:**")
                        st.code(tc["result"], language="text")

                st.write(reply)

            except Exception as e:
                if "Connection refused" in str(e):
                    reply = "⚠️ Cannot connect to Ollama. Run `ollama serve` in a terminal and try again."
                else:
                    reply = f"⚠️ Error: {e}"
                st.error(reply)
                tool_calls_display = []

    # Persist assistant message with tool display metadata
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
            "tool_calls_display": tool_calls_display,
        }
    )