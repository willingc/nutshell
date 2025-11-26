"""Load data from Discourse"""

import os
from pathlib import Path

import requests

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

token = os.environ.get("DISCOURSE_API_KEY")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
REQUEST_TIMEOUT = 30  # seconds

current_path = Path.cwd()
data_path = current_path / "data"


# get a topic
def get_topic(topic, filename):
    """Get a topic from Discourse API and save to JSON file.

    Parameters
    ----------
    topic : int
        The ID of the topic to retrieve.
    filename : Path
        Path where the JSON file should be saved.

    Notes
    -----
    The topic_id parameter is currently hardcoded to 104906 in the function body.
    """
    response = requests.get(
        f"https://discuss.python.org/t/{topic}.json?print=true",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    print(response.status_code, response.headers["Content-Type"])

    with Path.open(filename, "w", encoding="utf-8") as f:
        f.write(response.text)


if __name__ == "__main__":
    TOPIC_ID = 104906

    current_path = Path.cwd()
    data_path = current_path / "data"
    file_path = data_path / f"topic_{TOPIC_ID}.json"

    # Write a json file for a topic with all the posts
    get_topic(TOPIC_ID, file_path)

    data = read_json(file_path)
    posts = extract_posts(data)

    df = create_dataframe(posts)
    df = drop_columns(df)
    df = format_created_at(df)
    df = clean_cooked_posts(df)
    display_dataframe(df)

    write_post_files(df, data_path)
    write_posts_json(df, TOPIC_ID, data_path)
    write_posts_txt(df, data_path)
