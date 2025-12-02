"""Command-line interface for discuss-nutshell."""

from pathlib import Path

import typer
from google import genai

from discuss_nutshell.data_loader import load_topic
from discuss_nutshell.data_logger import init_db, log_interaction
from discuss_nutshell.visualize import create_visualization_app

app = typer.Typer()

current_path = Path.cwd()
data_path = current_path / "data"
DB_FILE = data_path / "posts_qa_logs.db"


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


def query_file(file: str | Path, query: str, model: str = "gemini-2.5-flash") -> str:
    """Query the file and return the response.

    Parameters
    ----------
    file : str | Path
        Path to the file to query.
    query : str
        The question or query about the file content.
    model : str, optional
        The Gemini model to use. Default is "gemini-2.5-flash".

    Returns
    -------
    str
        The response from the Gemini model.

    Notes
    -----
    Uses the Gemini API to generate responses. All interactions
    are logged to the SQLite database.
    """
    file_path = Path(file)
    if not file_path.exists():
        msg = f"File not found: {file}"
        raise FileNotFoundError(msg)

    filename = file_path.name
    file_text = extract_text_from_file(file_path)
    context = [file_text, query]

    client = genai.Client()
    response = client.models.generate_content(
        model=model,
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


@app.command()
def query(file: str, query: str, model: str = "gemini-2.5-flash") -> None:
    """Query a file."""
    response = query_file(file, query, model)
    print(response)


@app.command()
def visualize(json_file: str = "104906_all_posts.json") -> None:
    """Visualize Discourse posts as cards."""
    app = create_visualization_app(json_file)
    app.launch()


@app.command()
def load(
    topic_id: int, output: str = "data", process: bool = False, verbose: bool = False
) -> None:
    """Load a Discourse topic."""
    load_topic(topic_id, output, process, verbose)


def main() -> None:
    """Discuss Nutshell CLI."""
    init_db()
    app()


if __name__ == "__main__":
    main()
