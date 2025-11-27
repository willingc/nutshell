"""Command-line interface for discuss-nutshell."""

import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import requests
from google import genai

from discuss_nutshell.data_loader import get_topic
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


def cmd_query(args: argparse.Namespace) -> None:
    """Handle the query command.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments containing file and query.
    """
    try:
        response = query_file(args.file, args.query, args.model)
        print(response)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except (OSError, sqlite3.Error, ValueError, TypeError, KeyError) as e:
        print(f"Error querying file: {e}", file=sys.stderr)
        sys.exit(1)


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
        get_topic(args.topic_id, file_path)

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


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser with all subcommands and options.
    """
    parser = argparse.ArgumentParser(
        description="Query Discourse threads and summarize posts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query a file using Gemini API")
    query_parser.add_argument(
        "file",
        type=str,
        help="Path to the file to query",
    )
    query_parser.add_argument(
        "query",
        type=str,
        help="Question or query about the file content",
    )
    query_parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="Gemini model to use (default: gemini-2.5-flash)",
    )

    # Load command
    load_parser = subparsers.add_parser(
        "load", help="Load a Discourse topic from the API"
    )
    load_parser.add_argument(
        "topic_id",
        type=int,
        help="ID of the Discourse topic to load",
    )
    load_parser.add_argument(
        "--output",
        type=str,
        help="Output directory for saved files (default: ./data)",
    )
    load_parser.add_argument(
        "--process",
        action="store_true",
        help="Process and clean the loaded topic data",
    )
    load_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output during processing",
    )

    return parser


def main() -> None:
    """Main entry point for the CLI."""
    init_db()
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "query":
        cmd_query(args)
    elif args.command == "load":
        cmd_load(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
