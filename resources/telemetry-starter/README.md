# Research-Grade Persona Chat with Telemetry

> Personas that can **do things** — and you can **measure everything**

## What This Does

This starter extends the agentic chat app with **telemetry, logging, and session management**. Every message, tool call, and response time is logged to both structured JSON files and an SQLite database. Sessions can be replayed, exported, and analyzed.

- **Structured logging** — JSON-formatted events via Python's `logging` module
- **SQLite telemetry database** — queryable tables for sessions, messages, and tool calls
- **Response time measurement** — millisecond-precision timing on every LLM call
- **User feedback** — thumbs up / thumbs down on each response
- **Session replay** — view any past conversation step by step
- **Privacy controls** — opt-in telemetry and PII anonymization
- **Data export** — download any session as a JSON file

Built on: `streamlit-agentic-starter` + Python stdlib (`logging`, `sqlite3`)

**No new dependencies** — everything uses Python's standard library.

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Ollama installed and running (`ollama serve`)
- Pull a tool-calling model:
  ```bash
  ollama pull llama3.1
  ```

### 2. Install

```bash
cd resources/telemetry-starter
pip install -r requirements.txt
```

### 3. Run

```bash
streamlit run app_telemetry.py --server.address localhost
```

Or use the launcher scripts: `run.sh` (Mac/Linux) or `run.bat` (Windows).

You should see the app open in your browser with the title **"Research-Grade Persona Chat"** and a new **Telemetry** section in the sidebar.

---

## Files

| File | Description |
|------|-------------|
| `app_telemetry.py` | Main Streamlit app with telemetry hooks |
| `telemetry.py` | Telemetry infrastructure (logging + SQLite + session management) |
| `tools.py` | Tool definitions (same as agentic starter + `submit_feedback`) |
| `personas/*.yaml` | Persona configuration files |
| `requirements.txt` | Python dependencies |
| `EXERCISES.md` | Progressive exercises for the 2-week assignment |

### Generated at runtime

| File/Directory | Description |
|----------------|-------------|
| `logs/telemetry.log` | JSON-formatted application log (one event per line) |
| `telemetry.db` | SQLite database with sessions, messages, tool_calls tables |

---

## How It Works

```
User sends message
       |
       v
[Start timer]
ollama.chat(model, messages, tools=[...])
[Stop timer — record first_call_ms]
       |
       v
LLM returns tool_calls?
  |                    |
  No                  Yes
  |                    |
  v                    v
Display text     For each tool_call:
  |                1. [Start timer]
  |                2. Execute function(**args)
  |                3. [Stop timer — record duration_ms]
  |                4. Log to telemetry.db + telemetry.log
  |                5. Send results back to LLM
  |                      |
  v                      v
Log message        [Start timer]
to database        Second ollama.chat() call
  |                [Stop timer — record second_call_ms]
  v                      |
Show feedback            v
buttons            Log message to database
Show response      Show feedback buttons
time               Show total response time
```

### What Gets Logged

| Event | Where | Key Fields |
|-------|-------|------------|
| Session start/end | SQLite + JSON log | session_id, persona, model, timestamps |
| User message | SQLite + JSON log | content, session_id, timestamp |
| Assistant response | SQLite + JSON log | content, response_time_ms, timestamp |
| Tool call | SQLite + JSON log | tool_name, args, result, duration_ms |
| User feedback | SQLite + JSON log | thumbs_up / thumbs_down per message |

---

## Sidebar Features

| Section | What It Does |
|---------|-------------|
| **Persona** | Select and view persona profiles |
| **LLM Settings** | Model, temperature, top_p, max tokens |
| **Tools** | Enable/disable tools, see available tools |
| **Telemetry** | Enable/disable logging, toggle anonymization |
| **Execution Log** | Running history of tool calls with timing |
| **Session History** | List past sessions, replay, export JSON |

---

## Telemetry Architecture

### Three layers

1. **Python logging** (`logs/telemetry.log`) — JSON lines, one event per line. Great for streaming, grep, and debugging.
2. **SQLite database** (`telemetry.db`) — Structured tables with foreign keys. Great for SQL queries and analytics.
3. **Streamlit session state** — Real-time UI (tool_log, messages). Same as the agentic starter.

### Database schema

```
sessions (session_id PK, persona_name, model, started_at, ended_at)
    |
    +--< messages (id PK, session_id FK, role, content, response_time_ms, feedback, timestamp)
    |
    +--< tool_calls (id PK, session_id FK, tool_name, args_json, result, duration_ms, timestamp)
```

### Privacy controls

- **Enable telemetry** checkbox — turns all logging on/off
- **Anonymize inputs** checkbox — scrubs emails, phone numbers, and names before storing

---

## Model Requirements

Tool calling requires specific models:

| Model | Tool Calling |
|-------|-------------|
| `llama3.1` | Yes (recommended) |
| `mistral` | Yes |
| `qwen2.5` | Yes |
| `llama3.2` | **No** — does not support tool calling |
| `llama2`, `phi`, `gemma` | **No** |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No module named streamlit" | `pip install -r requirements.txt` |
| "No module named ollama" | `pip install ollama` |
| Connection error | Make sure Ollama is running: `ollama serve` |
| Tools never called | Use `llama3.1`, `mistral`, or `qwen2.5` — NOT `llama3.2` |
| Port already in use | `streamlit run app_telemetry.py --server.port 8502` |
| telemetry.db locked | Close other apps accessing the database |
| No logs appearing | Check that "Enable telemetry" is checked in sidebar |
| No sessions in history | Have a conversation first — sessions appear after messages are exchanged |

---

## What's New vs. the Agentic Starter

| Feature | Agentic Starter | Telemetry Starter |
|---------|----------------|-------------------|
| Tool calling | Yes | Yes |
| Execution log | In sidebar (session state) | In sidebar + SQLite + JSON file |
| Response timing | No | Yes (every LLM call) |
| User feedback | No | Yes (thumbs up/down) |
| Session persistence | No (lost on refresh) | Yes (SQLite database) |
| Session replay | No | Yes |
| Data export | No | Yes (JSON per session) |
| Privacy controls | No | Yes (opt-in + anonymization) |
| `submit_feedback` tool | No | Yes (new tool) |

---

## Next Steps

See **EXERCISES.md** for the 2-week assignment with progressive exercises covering:

1. Logging infrastructure
2. Telemetry data model and SQL queries
3. Session management with replay and export
4. Privacy and ethics (stretch)
5. Research dashboard (stretch)
