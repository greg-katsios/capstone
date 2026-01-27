# Student Exercises

Complete these exercises to learn how to use MCP for behavioral research.

---

## Exercise 1: Basic Interaction (30 minutes)

**Goal:** Learn how to test the MCP server

### Steps

1. **Start the inspector:**
   ```bash
   npx @modelcontextprotocol/inspector python participant_server.py
   ```

2. **View the participant profile:**
   - Click "Resources" tab
   - Click "participant://profile"
   - Read the demographics, personality, and values

3. **Test each question type:**

   **Yes/No Question:**
   ```json
   {
     "question": "Do you trust AI systems?",
     "question_type": "yes_no"
   }
   ```

   **Likert Scale:**
   ```json
   {
     "question": "How much do you support environmental policies?",
     "question_type": "likert"
   }
   ```

   **Open-ended:**
   ```json
   {
     "question": "What motivates you at work?",
     "question_type": "open_ended"
   }
   ```

4. **Check history:**
   - Click "get_interaction_history" tool
   - Call it (no parameters needed)
   - See all your interactions

### Questions to Answer

1. What personality trait is highest for this participant?
2. What personality trait is lowest?
3. How do their values (fairness, trust) compare?
4. Did their responses match their personality? How?

### Deliverable

Screenshot of successfully calling all 4 tools.

---

## Exercise 2: Trust Game Experiment (45 minutes)

**Goal:** Design and run a behavioral economics experiment

### Background

The trust game:
1. You send money to the participant (0-100)
2. The amount is tripled
3. Participant decides how much to return
4. This measures trust and fairness

### Steps

1. **Run baseline (no context):**
   ```json
   {
     "amount_sent": 50
   }
   ```
   Record how much they return.

2. **Run with positive framing:**
   ```json
   {
     "amount_sent": 50,
     "context": "Studies show cooperation benefits everyone"
   }
   ```
   Record how much they return.

3. **Run with negative framing:**
   ```json
   {
     "amount_sent": 50,
     "context": "There's a 50% chance all money will be lost"
   }
   ```
   Record how much they return.

4. **Try different amounts:**
   - Send $25, then $75
   - Does the amount you send change what they return?

### Questions to Answer

1. What percentage of the tripled amount did they return on average?
2. Did framing affect their decision?
3. Look at their fairness value (0.80). Does their behavior match?
4. Look at their trust value (0.65). Does their behavior match?

### Deliverable

1-page report with:
- Hypothesis
- Results table (condition vs. amount returned)
- Analysis

---

## Exercise 3: Modify the Participant (60 minutes)

**Goal:** Change personality and observe behavioral changes

### Steps

1. **Open `participant_server.py`**

2. **Find the PARTICIPANT dictionary (line 21)**

3. **Create 3 new profiles:**

   **Profile A - Very Agreeable:**
   ```python
   "agreeableness": 0.95,
   "fairness": 0.90,
   "trust": 0.85
   ```

   **Profile B - Not Agreeable:**
   ```python
   "agreeableness": 0.20,
   "fairness": 0.30,
   "trust": 0.25
   ```

   **Profile C - Balanced:**
   ```python
   "agreeableness": 0.50,
   "fairness": 0.50,
   "trust": 0.50
   ```

4. **For each profile:**
   - Restart the server
   - Run the same trust game (send $50)
   - Run the same survey question
   - Record results

### Questions to Answer

1. How did agreeableness affect trust game returns?
2. How did it affect survey responses?
3. Which trait had the biggest impact on behavior?

### Deliverable

Comparison table showing how each profile responded.

---

## Exercise 4: Add a New Tool (90 minutes)

**Goal:** Add the ultimatum game to the server

### The Ultimatum Game

- You propose how to split $100
- Participant accepts or rejects
- If they reject, both get $0

### Steps

1. **Add the tool definition (around line 142):**

```python
Tool(
    name="play_ultimatum_game",
    description="Propose a split of $100. Participant accepts or rejects.",
    inputSchema={
        "type": "object",
        "properties": {
            "your_share": {
                "type": "number",
                "description": "How much you want (0-100)"
            }
        },
        "required": ["your_share"]
    }
)
```

2. **Add the handler (around line 230):**

```python
elif name == "play_ultimatum_game":
    your_share = float(arguments["your_share"])
    their_share = 100 - your_share

    # Reject if offer is too unfair
    fairness = PARTICIPANT["values"]["fairness"]
    if their_share < (30 * fairness):  # Adjust threshold by fairness
        decision = "reject"
        reasoning = "This split is too unfair. I reject it."
        your_final = 0
        their_final = 0
    else:
        decision = "accept"
        reasoning = "This seems fair enough. I accept."
        your_final = your_share
        their_final = their_share

    return [TextContent(
        type="text",
        text=json.dumps({
            "your_proposal": your_share,
            "their_share": their_share,
            "decision": decision,
            "reasoning": reasoning,
            "your_final_amount": your_final,
            "their_final_amount": their_final
        }, indent=2)
    )]
```

3. **Test it:**
   - Restart the server
   - Try offering $50/$50
   - Try offering $80/$20
   - Try offering $95/$5

### Questions to Answer

1. At what split did they start rejecting?
2. Does this match their fairness value?
3. How could you improve this simulation?

### Deliverable

Working code + test results for 3 different splits.

---

## Exercise 5: Multiple Participants (90 minutes)

**Goal:** Create diverse participants and compare responses

### Steps

1. **Create 5 participant profiles** with different:
   - Ages (20, 30, 40, 50, 60)
   - Personalities (vary Big Five traits)
   - Values (vary fairness, trust)

2. **For each participant:**
   - Record demographics
   - Ask: "How much do you support UBI (universal basic income)?" (likert)
   - Play trust game with $50
   - Record results

3. **Analyze patterns:**
   - Does age correlate with trust game behavior?
   - Does openness correlate with UBI support?
   - Do any patterns emerge?

### Questions to Answer

1. Which traits predicted trust game returns?
2. Which traits predicted UBI support?
3. How much variance was there in responses?
4. What are the limitations of this simulation?

### Deliverable

Data table + 2-page analysis with charts.

---

## Exercise 6: Survey Design (45 minutes)

**Goal:** Use simulation to improve a real survey

### Steps

1. **Design a 5-question survey** on any topic you care about

2. **Test each question** with the participant

3. **Identify problems:**
   - Are questions clear?
   - Are response options appropriate?
   - Any leading questions?
   - Any confusing wording?

4. **Revise and retest:**
   - Rewrite unclear questions
   - Test again
   - Compare responses

### Questions to Answer

1. Which questions needed revision?
2. Why were they problematic?
3. How did you improve them?
4. What did this teach you about survey design?

### Deliverable

- Original survey
- Revised survey
- 1-page reflection on what you learned

---

## Exercise 7: Ethics Discussion (30 minutes)

**Goal:** Think critically about LLM simulation in research

### Discussion Questions

1. **Validity:** When is it appropriate to use LLM simulations vs. when is it not?

2. **Bias:** What biases might be present? How could they affect results?

3. **Transparency:** If you used this for pilot research, how would you report it?

4. **Limitations:** What can this NOT replace?

5. **Future:** How might LLM simulation change research?

### Deliverable

1-page position paper answering at least 3 questions above.

---

## Grading Rubric (For Instructors)

| Category | Points | What to Look For |
|----------|--------|------------------|
| **Completion** | 40% | Did they complete all steps? |
| **Analysis** | 30% | Did they answer questions thoughtfully? |
| **Critical Thinking** | 20% | Did they identify limitations? |
| **Code Quality** | 10% | For coding exercises, does code work? |

---

## Tips for Success

✅ **Do:**
- Read error messages carefully
- Test one thing at a time
- Keep notes on what you try
- Ask for help when stuck
- Think about limitations

❌ **Don't:**
- Skip the setup steps
- Treat simulations as real data
- Ignore ethical concerns
- Give up on first error
- Copy without understanding

---

## Need Help?

- **Setup issues:** See [SETUP.md](SETUP.md)
- **Don't understand MCP:** See [README.md](README.md)
- **Want to chat with AI:** See [TOOLS.md](TOOLS.md)
- **Stuck on code:** Ask your instructor!
