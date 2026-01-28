# Testing Tools Guide

**All options below are 100% free and open source** - perfect for students and educational use.

There are several ways to test your MCP server. Choose based on what you want to do.

---

## Quick Comparison

| Tool | Best For | Setup Time | Conversational? |
|------|----------|------------|-----------------|
| **MCP Inspector** | Learning, Testing | 0 min | No |
| **Ollama + ollmcp** | Research, Chat | 15 min | Yes |
| **Online Inspector** | Quick Demo | 0 min | No |

---

## Option 1: MCP Inspector (Recommended)

**Best for:** Testing tools, learning MCP, debugging

### How to Use

```bash
npx @modelcontextprotocol/inspector python participant_server.py
```

### What You Get

- Visual browser interface
- See all tools and resources
- Manual tool calling
- View JSON responses
- Debug mode

### Pros/Cons

✅ Zero setup
✅ Easy to understand
✅ Great for learning
❌ Not conversational
❌ Must manually call each tool

---

## Option 2: Ollama + ollmcp (For Natural Conversation)

**Best for:** Research, natural interaction, realistic usage

### Setup

1. **Install Ollama:**
   - Download from [ollama.ai](https://ollama.ai/)
   - Install for your OS

2. **Download a model:**
   ```bash
   ollama pull llama3.1
   ```

   **Important:** Only these models have good tool calling support:
   - llama3.1 ✅ (5GB) - **Best for tool calling**
   - mistral ✅ (4GB) - Good and efficient
   - qwen2.5 ✅ (4GB) - Also works well

   **Don't use:** llama3.2, llama2, phi, gemma (poor tool calling)

3. **Install MCP client:**
   ```bash
   pip install ollmcp
   ```

4. **Run it:**
   ```bash
   ollmcp --mcp-server participant_server.py --model llama3.1
   ```

   **Important:** Make sure your virtual environment is activated first!

   **If using different model:**
   ```bash
   ollmcp --mcp-server participant_server.py --model mistral
   ```

5. **First-time setup (in ollmcp):**

   When ollmcp starts, configure these settings:

   ```
   hil              # Disable Human-in-the-Loop for automatic tool execution
   ll 5             # Set loop limit to 5 for multi-step tasks
   show-tool-execution   # Show when tools are being called
   ```

   Then save your config:
   ```
   save-config
   ```

### What You Get

- Natural conversation with AI
- Automatic tool calling
- Realistic research experience
- 100% free and offline

**Note:** ollmcp works best with **tools** (conduct_survey, play_trust_game, etc.). To view the **participant profile resource**, use the MCP Inspector instead.

### Example Chat

**Good prompts that work well:**

```
You: Conduct a survey asking "Do you support climate action?" with question type yes_no

AI: [Calls conduct_survey tool]
Participant Response: Yes

You: Play a trust game by sending $50 to the participant

AI: [Calls play_trust_game with amount_sent: 50]
The participant received $150 and returned $91.25...

You: Ask them in an interview about their career satisfaction

AI: [Calls conduct_interview with topic: career satisfaction]
[Simulated interview response based on personality]

You: Show me the interaction history

AI: [Calls get_interaction_history]
[Shows all previous surveys, games, and interviews]
```

**Note:** The participant profile (demographics, personality, values) is a **resource**, not a tool. To view it:
- Use MCP Inspector: Resources → participant://profile → Read
- Or describe it manually when chatting: "The participant is 28 years old, non-binary, high openness (0.75)..."

### Pros/Cons

✅ Natural language
✅ AI decides which tools to use
✅ Realistic research workflow
✅ Completely free
❌ Requires more setup
❌ Needs 8GB+ RAM
❌ Model quality varies

---

## Option 3: Online Inspectors (No Install)

**Best for:** Quick demos, sharing with others

### Available Services

- [onlinemcpinspector.com](https://onlinemcpinspector.com/)
- [mcp.ziziyi.com/inspector](https://mcp.ziziyi.com/inspector)

### Pros/Cons

✅ Zero installation
✅ Works anywhere
❌ Can't test local servers easily
❌ Requires internet
❌ Less powerful

---

## Which Should I Use?

### For Learning (Week 1)
→ **Use MCP Inspector**
- Understand how MCP works
- See tools and resources clearly
- Learn by testing manually

### For Research (Week 2+)
→ **Use Ollama + ollmcp**
- Natural conversation
- Realistic workflow
- Better for experiments
- 100% free and open source
- No internet needed (after setup)

### For Quick Demo
→ **Use Online Inspector**
- No setup needed
- Show someone quickly

---

## Troubleshooting

### MCP Inspector

**"npx command not found"**
→ Install Node.js from [nodejs.org](https://nodejs.org/)

**Inspector doesn't open**
→ Manually go to `http://localhost:6789`

### Ollama + ollmcp

**"pip: command not found"**
→ Make sure your virtual environment is activated: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)

**"Model doesn't support tools"**
→ Use llama3.1, mistral, or qwen2.5 only (NOT llama3.2)

**"Connection refused"**
→ Start Ollama service: `ollama serve`

**"Out of memory"**
→ Use smaller model: `ollama pull mistral` (4GB, most efficient)

**"Cannot find participant_server.py"**
→ Make sure you run ollmcp from the mcp_demo directory

**"Model outputs JSON instead of calling tools"**
→ You're using a model without good tool support (like llama3.2)
→ Switch to llama3.1, mistral, or qwen2.5
→ Example: `ollmcp --mcp-server participant_server.py --model llama3.1`

**"Model called the wrong tool or made up data"**
→ Be more specific in your prompts
→ Example: Instead of "Get the profile", say "Conduct a survey asking about..."
→ Remember: Profile data is a resource (view in MCP Inspector), tools are for surveys/games/interviews

**"Tools execute but nothing happens"**
→ Check if Human-in-the-Loop (HIL) is enabled
→ Type `hil` to toggle it off, or press `d` at the confirmation prompt

---

## MCP Server Tools Reference

These are the research tools available in `participant_server.py`:

**Note:** When using the MCP Inspector, you'll see a form interface with text fields and dropdowns instead of having to write JSON manually. The JSON examples below show the parameter structure for reference.

### conduct_survey

Ask survey questions. Three types supported:

**In MCP Inspector:**
- Select "conduct_survey" from Tools dropdown
- **question** (text field): Enter your survey question
- **question_type** (dropdown): Select "likert", "yes_no", or "open_ended"

**Parameters (JSON reference):**
```json
{
  "question": "Your question here",
  "question_type": "likert"  // or "yes_no" or "open_ended"
}
```

**Example - Likert:**
```json
{
  "question": "How much do you support environmental policies?",
  "question_type": "likert"
}
```

**Response:** "4 - Agree" (1-5 scale)

**Example - Yes/No:**
```json
{
  "question": "Do you trust AI?",
  "question_type": "yes_no"
}
```

**Response:** "Yes" or "No"

**Example - Open-ended:**
```json
{
  "question": "What motivates you?",
  "question_type": "open_ended"
}
```

**Response:** Simulated text response (placeholder in current version)

---

### play_trust_game

Run a trust game experiment.

**In MCP Inspector:**
- Select "play_trust_game" from Tools dropdown
- **amount_sent** (number field): Enter amount to send (0-100)
- **context** (text field): Optional framing text (can leave empty)

**Rules:**
1. You send money (0-100)
2. Amount is tripled
3. Participant decides how much to return

**Parameters (JSON reference):**
```json
{
  "amount_sent": 50,
  "context": "This is a cooperation study"
}
```

**Response:**
```json
{
  "amount_you_sent": 50,
  "amount_received_by_participant": 150,
  "amount_returned_to_you": 91.25,
  "your_final_amount": 141.25,
  "participant_final_amount": 58.75,
  "participant_reasoning": "I believe in being fair...",
  "context_provided": "This is a cooperation study"
}
```

---

### conduct_interview

Have an open-ended conversation.

**In MCP Inspector:**
- Select "conduct_interview" from Tools dropdown
- **topic** (text field): Enter the interview topic

**Parameters (JSON reference):**
```json
{
  "topic": "Your topic here"
}
```

**Example:**
```json
{
  "topic": "career satisfaction"
}
```

**Response:** Simulated interview response based on personality

---

### get_interaction_history

View all past interactions.

**In MCP Inspector:**
- Select "get_interaction_history" from Tools dropdown
- Click "Call Tool" (no parameters needed)

**Response:** JSON array of all interactions (surveys, games, interviews)

---

## Participant Profile

**How to access in MCP Inspector:**
1. Click "Resources" tab
2. Click "participant://profile"
3. Click "Read" button

**Current participant:**
- **Age:** 28
- **Gender:** Non-binary
- **Education:** Bachelor's Degree
- **Occupation:** Software Developer

**Personality (0-1 scale):**
- Openness: 0.75 (high)
- Conscientiousness: 0.65 (moderate-high)
- Extraversion: 0.45 (moderate-low)
- Agreeableness: 0.70 (high)
- Neuroticism: 0.40 (moderate-low)

**Values:**
- Fairness: 0.80 (high)
- Trust: 0.65 (moderate-high)
- Risk aversion: 0.55 (moderate)

These influence all responses!

---

## Need More Help?

- **Setup problems:** [SETUP.md](SETUP.md)
- **Don't understand MCP:** [README.md](README.md)
- **Want exercises:** [EXERCISES.md](EXERCISES.md)
- **Teaching:** [TEACHING_GUIDE.md](TEACHING_GUIDE.md)
