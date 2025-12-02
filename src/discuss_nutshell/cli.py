"""Command-line interface for discuss-nutshell."""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
import typer
from google import genai

from discuss_nutshell.data_loader import load_topic
from discuss_nutshell.data_logger import init_db, log_interaction
from discuss_nutshell.preprocessor import (
    clean_cooked_posts,
    create_dataframe,
    drop_columns,
    extract_posts,
    format_created_at,
    read_json,
    write_post_files,
    write_posts_json,
    write_posts_txt,
)
from discuss_nutshell.utils import display_dataframe
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


def cmd_load(args: argparse.Namespace) -> None:
    """Handle the load command.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments containing topic_id and optional output path.
    """
    token = os.environ.get("DISCOURSE_API_KEY")
    if not token:
        print(
            "Error: DISCOURSE_API_KEY environment variable not set",
            file=sys.stderr,
        )
        sys.exit(1)

    output_path = Path(args.output) if args.output else data_path
    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / f"topic_{args.topic_id}.json"

    try:
        print(f"Loading topic {args.topic_id} from Discourse...")
        load_topic(args.topic_id, file_path)

        if args.process:
            print("Processing posts...")
            data = read_json(file_path)
            posts = extract_posts(data)

            df = create_dataframe(posts)
            df = drop_columns(df)
            df = format_created_at(df)
            df = clean_cooked_posts(df)

            if args.verbose:
                display_dataframe(df)

            print("Writing post files...")
            write_post_files(df, output_path)
            write_posts_json(df, args.topic_id, output_path)
            write_posts_txt(df, output_path)
            print(f"Processing complete. Files written to {output_path}")

        print(f"Topic data saved to {file_path}")
    except (
        requests.RequestException,
        json.JSONDecodeError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ) as e:
        print(f"Error loading topic: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Discuss Nutshell CLI."""
    init_db()
    app()


if __name__ == "__main__":
    main()
