# Testing Tools Guide

There are several free ways to test your MCP server. Choose based on what you want to do.

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
   ollama pull llama3.2
   ```

   **Important:** Only these models support MCP:
   - llama3.2 ✅ (2GB)
   - llama3.1 ✅ (4GB)
   - qwen2.5 ✅ (4GB)
   - mistral ✅ (4GB)

   Don't use: llama2, phi, gemma (old versions)

3. **Install MCP client:**
   ```bash
   npm install -g ollmcp
   ```

4. **Run it:**
   ```bash
   ollmcp --model llama3.2 --config mcp_config.json
   ```

### What You Get

- Natural conversation with AI
- Automatic tool calling
- Realistic research experience
- 100% free and offline

### Example Chat

```
You: Get the participant's profile

AI: I'll access the participant's profile for you.
[Automatically calls the resource]
This is a 28-year-old non-binary software developer...

You: Ask them if they support climate action

AI: I'll conduct a survey.
[Automatically calls conduct_survey with yes_no]
The participant responded: Yes

You: Play a trust game with $50

AI: I'll run the trust game.
[Automatically calls play_trust_game]
The participant returned $91.25...
```

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

### Ollama

**"Model doesn't support tools"**
→ Use llama3.2, qwen2.5, mistral, or command-r only

**"Connection refused"**
→ Start Ollama service: `ollama serve`

**"Out of memory"**
→ Use smaller model: `ollama pull llama3.2` (2GB)

---

## MCP Server Tools Reference

These are the research tools available in `participant_server.py`:

### conduct_survey

Ask survey questions. Three types supported:

**Parameters:**
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

**Parameters:**
```json
{
  "amount_sent": 50,
  "context": "Optional framing text"
}
```

**Rules:**
1. You send money (0-100)
2. Amount is tripled
3. Participant decides how much to return

**Example:**
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

**Parameters:**
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

View all past interactions. No parameters needed.

**Response:** JSON array of all interactions (surveys, games, interviews)

---

## Participant Profile

Access via Resources → `participant://profile`

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
