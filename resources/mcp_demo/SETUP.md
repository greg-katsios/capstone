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
1. Click "Resources" tab → Click "participant://profile" → See participant data
2. Click "Tools" tab → Click "conduct_survey"
3. In the JSON box, enter:
   ```json
   {
     "question": "Do you support environmental policies?",
     "question_type": "yes_no"
   }
   ```
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

```bash
ollama pull llama3.2
```

This downloads ~2GB. Wait for it to finish.

### Step 3: Install MCP client

```bash
npm install -g ollmcp
```

### Step 4: Run it

```bash
ollmcp --model llama3.2 --config mcp_config.json
```

Now you can chat:
```
You: Get the participant's profile
You: Conduct a survey asking about climate change
You: Play a trust game with $50
```

The AI will automatically call the right tools!

---

## What's in Each File?

| File | Purpose |
|------|---------|
| `participant_server.py` | The MCP server (the actual code) |
| `requirements.txt` | Python packages needed |
| `mcp_config.json` | Configuration for Ollama client |
| `test_server.py` | Simple test script (optional) |

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
