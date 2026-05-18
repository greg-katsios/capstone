# Agentic Chat Interface with Tool Calling

> Personas that can **do things**, not just talk

## What This Does

This demo extends the persona chat app with **tool calling**. Each persona can autonomously decide to call tools — saving memories, recalling facts, checking the time — and the UI shows every tool call transparently.

Built on: `streamlit-persona-starter` (persona chat) + concepts from `mcp_demo` (tool definitions)

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Ollama installed and running (`ollama serve`)
- **Important:** Pull `llama3.1` (not `llama3.2` — tool calling requires it):
  ```bash
  ollama pull llama3.1
  ```

### 2. Install

```bash
cd resources/streamlit-agentic-starter
pip install -r requirements.txt
```

### 3. Run

```bash
streamlit run app_agentic.py --server.address localhost
```

Or use the launcher scripts: `run.sh` (Mac/Linux) or `run.bat` (Windows).

---

## Files

| File | Description |
|------|-------------|
| `app_agentic.py` | Main Streamlit app with tool-calling loop |
| `tools.py` | Tool definitions (Python functions + registry) |
| `personas/*.yaml` | Persona files with tool configurations |
| `requirements.txt` | Python dependencies |

---

## How Tool Calling Works

```
User sends message
       |
       v
ollama.chat(model, messages, tools=[...])
       |
       v
LLM returns tool_calls?
  |                    |
  No                  Yes
  |                    |
  v                    v
Display text     For each tool_call:
                   1. Execute function(**args)
                   2. Show call + result in UI
                   3. Send results back to LLM
                        |
                        v
                   ollama.chat() again
                        |
                        v
                   Display final response
```

The LLM **decides on its own** when to call tools — you don't have to ask it to. That's what makes it "agentic."

---

## Available Tools

| Tool | Category | What It Does |
|------|----------|--------------|
| `save_memory` | Memory | Saves a fact (key/value) for later recall |
| `recall_memory` | Memory | Retrieves saved memories (all or by key) |
| `get_current_context` | Context | Returns current time + conversation stats |

---

## Adding Your Own Tools

1. **Define a function** in `tools.py` with type hints and a docstring:
   ```python
   def my_tool(query: str) -> str:
       """Search notes for a keyword.
       
       Args:
           query: The search term.
       
       Returns:
           Matching results.
       """
       # your implementation
       return "results"
   ```

2. **Register it** in `TOOL_FUNCTIONS` and `ALL_TOOLS` at the bottom of `tools.py`.

3. **Restart** the Streamlit app.

Ollama reads the function signature and docstring to generate the tool schema automatically.

---

## Connection to MCP

This demo uses Ollama's native tool calling with plain Python functions. The pattern is conceptually identical to MCP:

| This demo | MCP equivalent |
|-----------|---------------|
| Function with docstring | `Tool` with `inputSchema` |
| `TOOL_FUNCTIONS` dict | `@server.list_tools()` |
| `run_tool_call()` | `@server.call_tool()` |
| `tools` param in `chat()` | MCP tool discovery |

MCP formalizes this pattern over a protocol transport (stdio/SSE) so tools can run as separate processes. The mechanism is the same.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No module named streamlit" | `pip install -r requirements.txt` |
| "No module named ollama" | `pip install ollama` |
| Connection error | Make sure Ollama is running: `ollama serve` |
| Tools never called | Use `llama3.1`, `mistral`, or `qwen2.5` — NOT `llama3.2` |
| Port already in use | `streamlit run app_agentic.py --server.port 8502` |
| Model not found | `ollama pull llama3.1` |

---

## Model Requirements

Tool calling requires specific models. Supported:
- `llama3.1` (recommended, default)
- `mistral`
- `qwen2.5`

**Not supported:** `llama3.2`, `llama2`, `phi`, `gemma` (unreliable tool calling)
