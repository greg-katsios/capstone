# Setup Guide

Follow these steps to get the MCP Research Participant Demo running on your computer.

---

## Prerequisites

You need two things installed:

### 1. Python 3.10 or higher

Check if you have it:
```bash
python --version
```

If not, download from [python.org](https://www.python.org/downloads/)
- **Windows:** Check "Add Python to PATH" during installation
- **Mac/Linux:** May need to use `python3` instead of `python`

### 2. Node.js

Check if you have it:
```bash
node --version
```

If not, download from [nodejs.org](https://nodejs.org/) (get the LTS version)

---

## Installation Steps

### Step 1: Navigate to the folder

```bash
cd mcp_demo
```

### Step 2: Create virtual environment

```bash
python -m venv venv
```

### Step 3: Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install dependencies

```bash
pip install mcp
```

---

## Test Your Installation

### Method 1: MCP Inspector (Recommended)

The inspector is a browser tool for testing your server.

```bash
npx @modelcontextprotocol/inspector python participant_server.py
```

**What happens:**
1. Downloads inspector (first time only, ~5 seconds)
2. Starts your MCP server
3. Opens browser at `http://localhost:6789`

**What to do:**
1. Click "Resources" tab → Click "participant://profile" → Click "Read" → See participant data
2. Click "Tools" tab → Select "conduct_survey" from the dropdown
3. Fill in the form fields:
   - **question** (text field): Enter your survey question (e.g., "Do you support environmental policies?")
   - **question_type** (dropdown): Select "yes_no", "likert", or "open_ended"
4. Click "Call Tool"
5. See the response!

### Method 2: Simple Test Script

Just check if the server starts:

```bash
python participant_server.py
```

You'll see nothing happen - that's good! The server is waiting for input. Press `Ctrl+C` to stop it.

---

## Common Problems

### "python: command not found"
→ Try `python3` instead
→ Or reinstall Python with "Add to PATH" checked

### "npx: command not found"
→ Install Node.js from nodejs.org

### "Module 'mcp' not found"
→ Make sure you activated the virtual environment (see `(venv)` in prompt)
→ Run `pip install mcp` again

### Inspector doesn't open browser
→ Manually open `http://localhost:6789` in your browser

### Windows PowerShell activation fails
→ Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
→ Then try activating again

---

## Optional: Add Conversational AI

Want to talk naturally with the participant instead of clicking buttons?

### Step 1: Install Ollama

Download from [ollama.ai](https://ollama.ai/) and install.

### Step 2: Download a model

**Important:** Use llama3.1 (NOT llama3.2) for proper tool calling:

```bash
ollama pull llama3.1
```

This downloads ~5GB. Wait for it to finish.

**Alternative models that work well:**
- `ollama pull mistral` - Smaller (4GB), also works well
- `ollama pull qwen2.5` - Another good option

### Step 3: Install MCP client

```bash
pip install ollmcp
```

### Step 4: Run it

```bash
ollmcp --mcp-server participant_server.py --model llama3.1
```

**Note:** Make sure your virtual environment is activated so ollmcp can find the MCP package.

**If you chose a different model:**
```bash
ollmcp --mcp-server participant_server.py --model mistral
# or
ollmcp --mcp-server participant_server.py --model qwen2.5
```

Now you can chat:
```
You: Conduct a survey asking "Do you support climate action?" with question type yes_no
You: Play a trust game by sending $50 to the participant
You: Ask them in an interview about their career satisfaction
```

The AI will automatically call the right tools!

**Note:** To view the participant's profile (demographics, personality, values), use the MCP Inspector instead - it's stored as a resource, not a tool.

---

## What's in Each File?

| File | Purpose |
|------|---------|
| `participant_server.py` | The MCP server (the actual code) |
| `requirements.txt` | Python packages needed |
| `test_server.py` | Simple test script (optional) |
| `verify_functions.py` | Tests server functions work correctly |

---

## Verifying Everything Works

Run this checklist:

- [ ] Virtual environment activated (`(venv)` shows in terminal)
- [ ] `python --version` shows 3.10+
- [ ] `pip install mcp` completed without errors
- [ ] `python participant_server.py` starts (then Ctrl+C to stop)
- [ ] `npx @modelcontextprotocol/inspector python participant_server.py` opens browser
- [ ] You can see the participant profile in the inspector
- [ ] You can call the `conduct_survey` tool successfully

---

## Next Steps

✅ **You're all set!** Now go to [EXERCISES.md](EXERCISES.md) and start Exercise 1.

---

## Getting Help

**Setup problems?**
1. Read the "Common Problems" section above
2. Ask your instructor
3. Check [MCP official docs](https://modelcontextprotocol.io/)

**Don't know what to do next?**
1. Go to [EXERCISES.md](EXERCISES.md) - Start with Exercise 1
2. Read [TOOLS.md](TOOLS.md) - Learn about all available tools
