# MCP Research Participant Demo

> Simulate research participants with AI for behavioral research pilot studies

## What This Does

This demo creates a **simulated research participant** you can interview, survey, and run experiments with. Perfect for:
- Testing survey questions before real studies
- Pilot testing experimental designs
- Learning research methods
- Understanding how AI can help with research

**Cost:** $0 (completely free and open-source)

---

## Quick Start

### 1. Install (2 minutes)

```bash
# Install Python dependencies
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install mcp
```

### 2. Test It (1 minute)

```bash
# Run the MCP Inspector to test your server
npx @modelcontextprotocol/inspector python participant_server.py
```

This opens a browser where you can:
- View the participant's profile
- Conduct surveys
- Run trust game experiments
- Have interviews

### 3. Try It

In the inspector:
1. Click "Resources" → "participant://profile" to see who you're talking to
2. Click "Tools" → "conduct_survey"
3. Enter: `{"question": "Do you support climate action?", "question_type": "yes_no"}`
4. Click "Call Tool" and see the response!

---

## The Participant

Your simulated participant:
- **Demographics:** 28-year-old non-binary software developer
- **Personality:** High openness (0.75), high agreeableness (0.70), moderate extraversion (0.45)
- **Values:** High fairness (0.80), moderate trust (0.65)

These traits influence all their responses!

---

## Available Research Tools

| Tool | What It Does | Example |
|------|--------------|---------|
| `conduct_survey` | Ask survey questions | Likert scales, yes/no, open-ended |
| `play_trust_game` | Run behavioral economics experiments | Send money, see what they return |
| `conduct_interview` | Open-ended conversation | Ask about any topic |
| `get_interaction_history` | View all past interactions | See everything you've done |

---

## Full Documentation

**For Students:**
- **[SETUP.md](SETUP.md)** - Installation guide (start here!)
- **[EXERCISES.md](EXERCISES.md)** - 7 hands-on exercises
- **[TOOLS.md](TOOLS.md)** - Guide to all testing tools

**For Instructors:**
- **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** - 15-minute demo script
- **[TEACHING_GUIDE.md](TEACHING_GUIDE.md)** - Full teaching guide

---

## Important Notes

⚠️ **This is a SIMULATION** - Not real human data!
- Use for pilot testing and learning
- Always validate with real participants
- Be aware of AI biases
- Don't use as primary research data

✅ **Ethical Use:**
- Test survey questions
- Design experiments
- Learn research methods
- Generate hypotheses

---

## Need Help?

1. **Setup issues?** → Read [SETUP.md](SETUP.md)
2. **Don't know what to do?** → Try [EXERCISES.md](EXERCISES.md)
3. **Want to chat with AI?** → See [TOOLS.md](TOOLS.md) for Ollama setup
4. **Teaching this?** → Check [TEACHING_GUIDE.md](TEACHING_GUIDE.md)

---

## Requirements

- Python 3.10+
- Node.js (for testing)
- No API keys needed
- No subscriptions needed
- Works 100% offline (after setup)

---

**Made for students learning behavioral research methods** • Free & open-source
