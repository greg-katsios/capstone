# Exercises — Telemetry, Logging & Session Management

Complete these exercises to build research-grade telemetry into your persona chat app.

**Time budget:** 2 weeks. Exercises 1–3 are required. Exercises 4–5 are stretch goals.

**Deliverable:** Research Platform v1 with Telemetry — comprehensive logging, extended database schema, session replay, privacy controls, export capability, and telemetry documentation.

---

## Exercise 1: Logging Infrastructure (60 minutes)

**Goal:** Understand and extend the structured logging system.

### Steps

1. **Run the starter app:**
   ```bash
   streamlit run app_telemetry.py --server.address localhost
   ```

2. **Have a short conversation** (5+ messages) with any persona. Try to trigger tool calls — say "My name is Alex" or "What time is it?"

3. **Inspect the JSON log file:**
   - Open `logs/telemetry.log` in a text editor
   - Each line is a single JSON object
   - Identify these event types: `session_started`, `message_logged`, `tool_call_logged`, `feedback_logged`

4. **Inspect the SQLite database:**
   ```python
   import sqlite3

   conn = sqlite3.connect("telemetry.db")
   conn.row_factory = sqlite3.Row

   print("=== Sessions ===")
   for row in conn.execute("SELECT * FROM sessions"):
       print(dict(row))

   print("\n=== Messages ===")
   for row in conn.execute("SELECT * FROM messages LIMIT 10"):
       print(dict(row))

   print("\n=== Tool Calls ===")
   for row in conn.execute("SELECT * FROM tool_calls"):
       print(dict(row))
   ```

5. **Add a new log event — persona switches:**
   - Open `telemetry.py`
   - Add a `log_persona_switch(self, session_id, old_persona, new_persona)` method
   - It should INSERT into the JSON log with event `"persona_switched"`
   - Hook it into `app_telemetry.py` in the persona-switch block (look for `if st.session_state.active_persona != persona_id`)

6. **Verify your new event appears** in `logs/telemetry.log` after switching personas.

### Questions to Answer

1. What is the difference between the JSON log file and the SQLite database? When would you use one vs. the other?
2. What fields are captured in a `message_logged` event? Why log `content_length` instead of the full content in the JSON log?
3. Why does the logger use `json.dumps()` for log output instead of plain text?
4. What happens to the log file when you restart the app — does it append or overwrite?

### Deliverable

Screenshot of your log file showing at least 3 different event types, plus the code for your `log_persona_switch` method.

---

## Exercise 2: Telemetry Data Model (90 minutes)

**Goal:** Extend the database schema and write analysis queries.

### Steps

1. **Study the existing schema:**
   - Open `telemetry.py` and read the `_init_database()` method
   - Draw an ER diagram showing: `sessions` --< `messages`, `sessions` --< `tool_calls`
   - Note the foreign key relationships

2. **Add a new table — `feedback`:**
   ```sql
   CREATE TABLE IF NOT EXISTS feedback (
       id          INTEGER PRIMARY KEY AUTOINCREMENT,
       session_id  TEXT NOT NULL,
       message_id  INTEGER NOT NULL,
       rating      TEXT NOT NULL,
       comment     TEXT,
       timestamp   TEXT NOT NULL,
       FOREIGN KEY (session_id) REFERENCES sessions(session_id),
       FOREIGN KEY (message_id) REFERENCES messages(id)
   );
   ```
   - Add this to `_init_database()` in `telemetry.py`
   - Update the `log_feedback()` method to INSERT into this table (in addition to updating the `messages.feedback` column)
   - Wire the thumbs-up/thumbs-down buttons in `app_telemetry.py` to populate this table

3. **Write analysis queries** (test them in a Python script or SQLite viewer):

   **a. Average response time per persona:**
   ```sql
   SELECT s.persona_name, AVG(m.response_time_ms) AS avg_ms
   FROM messages m
   JOIN sessions s ON m.session_id = s.session_id
   WHERE m.role = 'assistant' AND m.response_time_ms IS NOT NULL
   GROUP BY s.persona_name;
   ```

   **b. Most frequently called tools:**
   ```sql
   SELECT tool_name, COUNT(*) AS call_count
   FROM tool_calls
   GROUP BY tool_name
   ORDER BY call_count DESC;
   ```

   **c. Session duration:**
   ```sql
   SELECT session_id, persona_name,
          (julianday(ended_at) - julianday(started_at)) * 86400 AS duration_seconds
   FROM sessions
   WHERE ended_at IS NOT NULL;
   ```

   **d. Feedback distribution per persona:**
   ```sql
   SELECT s.persona_name, m.feedback, COUNT(*) AS count
   FROM messages m
   JOIN sessions s ON m.session_id = s.session_id
   WHERE m.feedback IS NOT NULL
   GROUP BY s.persona_name, m.feedback;
   ```

4. **Create an analytics page (optional):**
   - Create `pages/analytics.py` (Streamlit multipage app)
   - Display query results using `st.metric()`, `st.bar_chart()`, or `st.dataframe()`
   - Tip: Streamlit auto-discovers pages in the `pages/` directory

### Questions to Answer

1. Why use foreign keys in the schema? What happens if you try to insert a message with a nonexistent session_id?
2. What index would you add to speed up "find all messages for a session"?
3. How would you add a `topics` table to track what users ask about? What columns would it need?
4. What are the tradeoffs between SQLite and a JSON file for analytics?

### Deliverable

Updated ER diagram, the 4 working SQL queries with sample output, and (optional) analytics page screenshot.

---

## Exercise 3: Session Management (90 minutes)

**Goal:** Implement full session lifecycle with replay and export.

### Steps

1. **Test session creation and switching:**
   - Start the app, chat for a few messages
   - Switch personas — check the Session History sidebar to verify a new session starts
   - Check that the old session appears in the list with a message count

2. **Improve session replay:**
   The starter includes basic replay. Enhance it:
   - Show tool calls inline within the replay (currently shown separately at the bottom)
   - Display response time for each assistant message
   - Add a "Session summary" header with: persona, model, start time, duration, message count

3. **Test JSON export:**
   - Click "Export" on any session in the Session History
   - Download the JSON file and open it
   - Verify it contains: session metadata, all messages (with timestamps), all tool calls (with timing)

4. **Add session metadata to the sidebar:**
   - Show the current session ID at the top of the Telemetry section
   - Calculate and display: total messages, total tool calls, average response time
   - Update these stats in real time as the conversation progresses

5. **Make session IDs human-readable:**
   - Modify `start_session()` in `telemetry.py` to generate IDs like `tutor-20260422-a3f2` (persona prefix + date + short hash)
   - Update all code that references session IDs
   - Test that replay and export still work

### Questions to Answer

1. Why is a session ID important for research? What would go wrong without one?
2. What happens if the app crashes mid-session — is the data lost? How would you make it more robust?
3. How would you implement session persistence across devices (not just the local SQLite file)?
4. What metadata would a researcher want beyond what we currently capture?

### Deliverable

Working session replay with inline tool calls, JSON export of a 10+ message session, and answers to the questions.

---

## Exercise 4: Privacy & Ethics (45 minutes) — Stretch

**Goal:** Implement responsible data collection practices.

### Steps

1. **Test the anonymization toggle:**
   - Enable "Anonymize inputs" in the sidebar
   - Send messages containing: an email address, a phone number, and "my name is Alex"
   - Query the database — verify the stored content shows `[EMAIL]`, `[PHONE]`, `[NAME]` instead of real data

2. **Improve the anonymization patterns:**
   Add regex patterns for at least 3 new PII types:
   - Street addresses (e.g., "123 Main St")
   - Dates of birth (e.g., "born on 03/15/1995")
   - Student IDs (e.g., "my student ID is A12345678")

   Write a test file `test_telemetry.py`:
   ```python
   from telemetry import TelemetryLogger

   tl = TelemetryLogger(db_path=":memory:", log_dir="test_logs")

   # Test existing patterns
   assert "[EMAIL]" in tl.anonymize_text("email me at alex@example.com")
   assert "[PHONE]" in tl.anonymize_text("call 555-123-4567")
   assert "[NAME]" in tl.anonymize_text("my name is Alex")

   # Test your new patterns
   # assert "[ADDRESS]" in tl.anonymize_text("I live at 123 Main St")
   # ... add your tests here

   print("All tests passed!")
   ```

3. **Add a consent banner:**
   - On first app load, show `st.info()` explaining what data is collected
   - Add an "I understand" button that sets `st.session_state.consent_given = True`
   - Only enable telemetry after consent is given
   - Store consent status in session state so it persists during the session

4. **Add a data retention policy:**
   - Add a method `delete_sessions_older_than(days: int)` to `TelemetryLogger`
   - It should DELETE from `tool_calls`, `messages`, and `sessions` (in that order, respecting foreign keys)
   - Add a sidebar control for retention period (7, 30, 90 days)
   - Run cleanup automatically on app startup

### Questions to Answer

1. Is regex-based PII scrubbing sufficient for real research? What would you use in production?
2. What would an IRB (Institutional Review Board) require for collecting this kind of data from real users?
3. How does GDPR's "right to be forgotten" apply to telemetry databases?
4. What is the difference between anonymization and pseudonymization?

### Deliverable

Improved anonymization with 3+ new patterns, consent banner implementation, and a 1-page ethics reflection.

---

## Exercise 5: Research Dashboard (120 minutes) — Stretch

**Goal:** Create a complete analysis pipeline from telemetry data.

### Steps

1. **Generate enough data:**
   - Have 5+ conversations across all 3 personas (at least 10 messages each)
   - Use tools in each conversation
   - Provide feedback (thumbs up/down) on at least 10 responses

2. **Build a dashboard (`pages/dashboard.py`):**
   - **Response time distribution** — histogram of response_time_ms across all messages
   - **Tool usage by persona** — bar chart showing which tools each persona calls
   - **Feedback summary** — positive vs. negative rates per persona
   - **Session timeline** — when sessions happened, how long they lasted
   - **Key metrics** — use `st.metric()` for: total sessions, total messages, average response time, feedback score

3. **Export for external analysis:**
   - Add an "Export all sessions" button
   - Output format: JSON or CSV suitable for pandas / Excel
   - Include fields: session_id, persona, message_count, avg_response_ms, tool_count, feedback_score

4. **Write a research memo (1–2 pages):**
   - What patterns did you observe across personas?
   - Which persona got the best feedback? Why do you think?
   - Did response time correlate with message length or tool use?
   - What would you change about the telemetry design for a real study?

### Deliverable

Dashboard screenshot, exported dataset, and 1–2 page research memo.

---

## Grading Rubric

| Category | Weight | What to Look For |
|----------|--------|------------------|
| **Logging Infrastructure** (Ex 1) | 25% | JSON logs working, new event added, questions answered |
| **Data Model** (Ex 2) | 25% | Schema extended, 4 queries working, ER diagram complete |
| **Session Management** (Ex 3) | 25% | Replay enhanced, export working, human-readable IDs |
| **Analysis & Reflection** | 15% | Thoughtful answers, clear writing, research awareness |
| **Code Quality** | 10% | Clean code, good comments, error handling |

---

## Tips for Success

**Do:**
- Start by running the app and exploring what already works
- Read `telemetry.py` before modifying it — trace the flow from a message to the database
- Test with small conversations first
- Check your database after each change (`sqlite3` CLI or DB Browser for SQLite)
- Think about what a researcher would want to measure

**Don't:**
- Store real PII in your test data
- Skip the privacy questions — they matter for your capstone
- Ignore error handling (database connections can fail)
- Forget to close sessions (check for orphaned sessions with `ended_at IS NULL`)
- Over-engineer — this is a teaching tool, not production software

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `telemetry.db` is locked | Close other programs accessing the database, restart the app |
| No sessions in history | Check "Enable telemetry" is on, have a conversation first |
| Anonymization not working | Verify the "Anonymize inputs" checkbox, test regex at regex101.com |
| Export file is empty | Make sure the session has messages, check session_id matches |
| `pages/` directory not detected | Restart Streamlit — it scans for pages on startup |

---

## Resources

- [Python logging documentation](https://docs.python.org/3/library/logging.html)
- [Python logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [SQLite documentation](https://www.sqlite.org/docs.html)
- [Streamlit session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Streamlit multipage apps](https://docs.streamlit.io/develop/concepts/multipage-apps)
- [DB Browser for SQLite](https://sqlitebrowser.org/) — visual database explorer
- [regex101.com](https://regex101.com/) — test regex patterns interactively
