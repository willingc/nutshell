import json
from pathlib import Path
from typing import Any

import pandas as pd

from discuss_nutshell.utils import clean_html, format_date


def read_json(file_path):
    """Read JSON file.

    Parameters
    ----------
    file_path : Path
        Path to the JSON file to read.

    Returns
    -------
    dict | list
        Parsed JSON data.
    """
    with Path.open(file_path, encoding="utf-8") as f:
        return json.load(f)


def extract_posts(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract individual posts from post stream.

    Parameters
    ----------
    data : dict[str, Any]
        Discourse topic data containing post_stream.

    Returns
    -------
    list[dict[str, Any]]
        List of post dictionaries from the post_stream.
    """
    return data["post_stream"]["posts"]


def write_json(data, file_path):
    """Write JSON file.

    Parameters
    ----------
    data : dict | list
        Data to write as JSON.
    file_path : Path
        Path where the JSON file should be written.
    """
    with Path.open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def create_dataframe(posts):
    """Create dataframe from posts.

    Parameters
    ----------
    posts : list[dict[str, Any]]
        List of post dictionaries.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all posts.
    """
    return pd.DataFrame(posts)


def drop_columns(df):
    """Drop columns from dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to process.

    Returns
    -------
    pd.DataFrame
        DataFrame with specified columns removed.

    Notes
    -----
    Drops a predefined set of columns that are not needed for analysis.
    Uses errors="ignore" to handle missing columns gracefully.
    """
    return df.drop(
        columns=[
            "avatar_template",
            "updated_at",
            "reply_count",
            "reply_to_post_number",
            "quote_count",
            "incoming_link_count",
            "reads",
            "readers_count",
            "score",
            "yours",
            "primary_group_name",
            "flair_name",
            "flair_url",
            "flair_bg_color",
            "flair_color",
            "flair_group_id",
            "badges_granted",
            "version",
            "can_edit",
            "can_delete",
            "can_recover",
            "can_see_hidden_post",
            "can_wiki",
            "link_counts",
            "read",
            "user_title",
            "title_is_group",
            "bookmarked",
            "actions_summary",
            "moderator",
            "admin",
            "staff",
            "user_id",
            "hidden",
            "trust_level",
            "deleted_at",
            "user_deleted",
            "edit_reason",
            "can_view_edit_history",
            "wiki",
            "post_url",
            "can_accept_answer",
            "can_unaccept_answer",
            "accepted_answer",
            "topic_accepted_answer",
            "can_vote",
            "reply_to_user",
        ],
        errors="ignore",
    )


def format_created_at(df):
    """Format created at date.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'created_at' column containing ISO date strings.

    Returns
    -------
    pd.DataFrame
        DataFrame with 'created_at' column formatted to readable date strings.
    """
    df["created_at"] = df["created_at"].apply(format_date)
    return df


def clean_cooked_posts(df):
    """Clean post's HTML content.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'cooked' column containing HTML content.

    Returns
    -------
    pd.DataFrame
        DataFrame with new 'clean_cooked' column containing cleaned text.
    """
    df["clean_cooked"] = df["cooked"].apply(clean_html)
    return df


def write_post_files(df, output_path):
    """Write post files to output directory.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing posts with columns: id, name, created_at,
        post_number, and clean_cooked.
    output_path : Path
        Directory where individual post files should be written.

    Notes
    -----
    Creates individual text files named 'post_{id}.txt' for each post
    containing author, creation date, post number, and clean content.
    """
    for _index, row in df.iterrows():
        post_id = row["id"]
        author = row["name"]
        created_at = row["created_at"]
        number = row["post_number"]
        clean_content = row["clean_cooked"]

        with Path.open(output_path / f"post_{post_id}.txt", "w", encoding="utf-8") as f:
            f.write(f"Author: {author}\n")
            f.write(f"Created at: {created_at}\n")
            f.write(f"Number: {number}\n")
            f.write(f"Clean content: {clean_content}\n")


def write_posts_json(df: pd.DataFrame, topic_id: int, output_path: Path) -> None:
    """Write all posts from a topic to a single JSON file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing posts with columns: id, name, created_at,
        post_number, and clean_cooked.
    topic_id : int
        ID of the topic.
    output_path : Path
        Directory where the JSON file should be written.

    Notes
    -----
    Creates a single JSON file named '{topic_id}_all_posts.json' containing
    all posts as a list of dictionaries.
    """
    # Initialize an empty list to store post dictionaries
    posts_list = []

    # Iterate through DataFrame rows
    for _index, row in df.iterrows():
        # Extract data from each row
        post_id = row["id"]
        author = row["name"]
        number = row["post_number"]
        created_at = row["created_at"]
        clean_content = row["clean_cooked"]

        # Create a dictionary for each post
        post_dict = {
            "id": post_id,
            "author": author,
            "number": number,
            "created_at": created_at,
            "clean_content": clean_content,
        }

        # Append each post dictionary to the list
        posts_list.append(post_dict)

    # Write the list to a JSON file
    output_file = output_path / f"{topic_id}_all_posts.json"
    with Path.open(output_file, "w", encoding="utf-8") as f:
        json.dump(posts_list, f, indent=2)


def write_posts_txt(df, output_path):
    """Write post files to output directory.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing posts with columns: id, name, created_at,
        post_number, and clean_cooked.
    output_path : Path
        Directory where the text file should be written.

    Notes
    -----
    Appends all posts to a single file named 'all_posts.txt' in the output
    directory. Each post includes ID, author, creation date, post number,
    and clean content.
    """
    for _index, row in df.iterrows():
        post_id = row["id"]
        author = row["name"]
        created_at = row["created_at"]
        number = row["post_number"]
        clean_content = row["clean_cooked"]

        with Path.open(output_path / "all_posts.txt", "a", encoding="utf-8") as f:
            f.write(f"ID: {post_id}\n")
            f.write(f"Author: {author}\n")
            f.write(f"Created at: {created_at}\n")
            f.write(f"Number: {number}\n")
            f.write(f"Clean content: {clean_content}\n")
