"""Log data to SQLite database."""

import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

current_path = Path.cwd()
data_path = current_path / "data"
DB_FILE = data_path / "posts_qa_logs.db"


def init_db() -> None:
    """Initialize the SQLite database with interactions table.

    Notes
    -----
    Creates a table named 'interactions' if it doesn't exist with columns:
    id, timestamp, post_name, query, full_context, and response.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS interactions (
                 id TEXT PRIMARY KEY,
                 timestamp TEXT,
                 post_name TEXT,
                 query TEXT,
                 full_context TEXT,
                 response TEXT)""")
    conn.commit()
    conn.close()


def log_interaction(
    filename: str, query: str, full_context: str, response: str
) -> None:
    """Log the interaction to SQLite database.

    Parameters
    ----------
    filename : str
        Name of the file that was queried.
    query : str
        The user's query/question.
    full_context : str
        The full context (file content + query) sent to the model.
    response : str
        The response from the model.

    Notes
    -----
    Generates a unique UUID for each interaction and records the current
    timestamp in UTC.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    interaction_id = str(uuid.uuid4())
    timestamp = datetime.now(UTC).isoformat()
    c.execute(
        "INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?)",
        (interaction_id, timestamp, filename, query, full_context, response),
    )
    conn.commit()
    conn.close()
