"""Get a file and query it using Gemini API and Gradio UI."""

import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

import gradio as gr
from google import genai

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


init_db()


# initialize the Gemini client
client = genai.Client()


def extract_text_from_file(file_path: str | Path) -> str:
    """Extract text from a file.

    Parameters
    ----------
    file_path : str | Path
        Path to the file to read.

    Returns
    -------
    str
        The contents of the file as a string.
    """
    with Path(file_path).open(encoding="utf-8") as f:
        return f.read()


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


def query_file(file: str | None, query: str) -> str:
    """Query the file and return the response.

    Parameters
    ----------
    file : str | None
        Path to the file to query. If None, returns an error message.
    query : str
        The question or query about the file content.

    Returns
    -------
    str
        The response from the Gemini model, or an error message if no file
        is provided.

    Notes
    -----
    Uses the Gemini 2.5 Flash model to generate responses. All interactions
    are logged to the SQLite database.
    """
    if file is None:
        return "Please upload a file."

    filename = Path(file).name
    file_text = extract_text_from_file(file)
    context = [file_text, query]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=context,
    )

    response_text = str(response.text)
    log_interaction(
        filename=filename,
        query=query,
        full_context=context[0] + context[1],
        response=response_text,
    )

    return response_text


# Gradio interface setup
with gr.Blocks() as app:
    file_upload = gr.File(label="Upload file", type="filepath")
    query_input = gr.Textbox(label="Ask a question about the post")
    query_button = gr.Button("Submit")
    output = gr.Textbox(label="Answer", lines=10)

    query_button.click(query_file, inputs=[file_upload, query_input], outputs=output)

if __name__ == "__main__":
    app.launch()
