"""
Telemetry infrastructure for the Research-Grade Persona Chat.

Combines two storage backends:
  1. Python logging  -> JSON-formatted log file (logs/telemetry.log)
  2. SQLite database -> structured tables     (telemetry.db)

Both use only the Python standard library — no extra dependencies.

Usage:
    tl = TelemetryLogger()
    sid = tl.start_session(persona_name="Tutor Taylor", model="llama3.1")
    tl.log_message(sid, role="user", content="Hi!")
    tl.log_message(sid, role="assistant", content="Hello!", response_time_ms=342.5)
    tl.log_tool_call(sid, "save_memory", {"key": "name"}, "Saved", 12.3)
    tl.end_session(sid)
"""

import json
import logging
import os
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

# ── Defaults ───────────────────────────────────────────────────

LOG_DIR = "logs"
LOG_FILE = "logs/telemetry.log"
DB_PATH = "telemetry.db"


# ── JSON log formatter ─────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """Formats each log record as a single JSON line.

    The ``data`` field comes from ``extra={"data": {...}}`` passed to
    the logger call.  If omitted it defaults to an empty dict.
    """

    def format(self, record):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
            "data": getattr(record, "data", {}),
        }
        return json.dumps(entry, default=str)


# ── TelemetryLogger ───────────────────────────────────────────

class TelemetryLogger:
    """Facade that writes every event to both the JSON log and SQLite."""

    def __init__(self, db_path: str = DB_PATH, log_dir: str = LOG_DIR):
        self.db_path = db_path
        self.log_dir = log_dir
        self.logger = self._setup_logging()
        self.conn = self._init_database()

    # ── Private setup ──────────────────────────────────────────

    def _setup_logging(self) -> logging.Logger:
        os.makedirs(self.log_dir, exist_ok=True)

        logger = logging.getLogger("telemetry")
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            fh = logging.FileHandler(
                os.path.join(self.log_dir, "telemetry.log"),
                encoding="utf-8",
            )
            fh.setFormatter(JSONFormatter())
            logger.addHandler(fh)

        return logger

    def _init_database(self) -> sqlite3.Connection:
        # check_same_thread=False is required because Streamlit
        # may call back into this object from different threads.
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id   TEXT PRIMARY KEY,
                persona_name TEXT NOT NULL,
                model        TEXT DEFAULT '',
                started_at   TEXT NOT NULL,
                ended_at     TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id       TEXT NOT NULL,
                role             TEXT NOT NULL,
                content          TEXT NOT NULL,
                response_time_ms REAL,
                feedback         TEXT,
                timestamp        TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );

            CREATE TABLE IF NOT EXISTS tool_calls (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id    TEXT NOT NULL,
                tool_name     TEXT NOT NULL,
                args_json     TEXT NOT NULL,
                result        TEXT NOT NULL,
                duration_ms   REAL,
                persona_name  TEXT DEFAULT '',
                timestamp     TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
        """)
        conn.commit()
        return conn

    # ── Session lifecycle ──────────────────────────────────────

    def start_session(self, persona_name: str, model: str = "") -> str:
        session_id = uuid.uuid4().hex[:12]
        now = datetime.now().isoformat()

        self.conn.execute(
            "INSERT INTO sessions (session_id, persona_name, model, started_at) "
            "VALUES (?, ?, ?, ?)",
            (session_id, persona_name, model, now),
        )
        self.conn.commit()

        self.logger.info(
            "session_started",
            extra={"data": {
                "session_id": session_id,
                "persona_name": persona_name,
                "model": model,
            }},
        )
        return session_id

    def end_session(self, session_id: str) -> None:
        now = datetime.now().isoformat()
        self.conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE session_id = ?",
            (now, session_id),
        )
        self.conn.commit()

        self.logger.info(
            "session_ended",
            extra={"data": {"session_id": session_id}},
        )

    # ── Event logging ──────────────────────────────────────────

    def log_message(
        self,
        session_id: str,
        role: str,
        content: str,
        response_time_ms: float | None = None,
        anonymize: bool = False,
    ) -> None:
        stored_content = self.anonymize_text(content) if anonymize else content
        now = datetime.now().isoformat()

        self.conn.execute(
            "INSERT INTO messages "
            "(session_id, role, content, response_time_ms, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, role, stored_content, response_time_ms, now),
        )
        self.conn.commit()

        self.logger.info(
            "message_logged",
            extra={"data": {
                "session_id": session_id,
                "role": role,
                "content_length": len(content),
                "response_time_ms": response_time_ms,
            }},
        )

    def log_tool_call(
        self,
        session_id: str,
        tool_name: str,
        args: dict,
        result: str,
        duration_ms: float,
        persona_name: str = "",
    ) -> None:
        now = datetime.now().isoformat()
        args_json = json.dumps(args, default=str)

        self.conn.execute(
            "INSERT INTO tool_calls "
            "(session_id, tool_name, args_json, result, duration_ms, "
            "persona_name, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, tool_name, args_json, result, duration_ms,
             persona_name, now),
        )
        self.conn.commit()

        self.logger.info(
            "tool_call_logged",
            extra={"data": {
                "session_id": session_id,
                "tool_name": tool_name,
                "duration_ms": duration_ms,
            }},
        )

    def log_feedback(
        self,
        session_id: str,
        message_index: int,
        feedback: str,
    ) -> None:
        """Record thumbs-up / thumbs-down on the Nth message in a session."""
        rows = self.conn.execute(
            "SELECT id FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()

        if 0 <= message_index < len(rows):
            msg_id = rows[message_index]["id"]
            self.conn.execute(
                "UPDATE messages SET feedback = ? WHERE id = ?",
                (feedback, msg_id),
            )
            self.conn.commit()

        self.logger.info(
            "feedback_logged",
            extra={"data": {
                "session_id": session_id,
                "message_index": message_index,
                "feedback": feedback,
            }},
        )

    # ── Query helpers ──────────────────────────────────────────

    def get_sessions(self) -> list[dict]:
        rows = self.conn.execute("""
            SELECT s.session_id, s.persona_name, s.model,
                   s.started_at, s.ended_at,
                   COUNT(m.id) AS message_count
            FROM sessions s
            LEFT JOIN messages m ON m.session_id = s.session_id
            GROUP BY s.session_id
            ORDER BY s.started_at DESC
        """).fetchall()
        return [dict(r) for r in rows]

    def get_session_messages(self, session_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT role, content, response_time_ms, feedback, timestamp "
            "FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_session_tool_calls(self, session_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT tool_name, args_json, result, duration_ms, "
            "persona_name, timestamp "
            "FROM tool_calls WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def export_session(self, session_id: str) -> str:
        session_row = self.conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()

        if session_row is None:
            return json.dumps({"error": f"Session {session_id} not found"})

        return json.dumps({
            "session": dict(session_row),
            "messages": self.get_session_messages(session_id),
            "tool_calls": self.get_session_tool_calls(session_id),
        }, indent=2, default=str)

    # ── Privacy ────────────────────────────────────────────────

    def anonymize_text(self, text: str) -> str:
        """Replace common PII patterns with placeholders.

        This is a teaching example — production systems should use
        NER models or dedicated PII-detection libraries.
        """
        # Email addresses
        text = re.sub(r"\b[\w.-]+@[\w.-]+\.\w+\b", "[EMAIL]", text)
        # US phone numbers (xxx-xxx-xxxx, xxx.xxx.xxxx, xxxxxxxxxx)
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]", text)
        # "my name is <word>"
        text = re.sub(
            r"\bmy name is (\w+)\b", "my name is [NAME]", text, flags=re.I,
        )
        return text
