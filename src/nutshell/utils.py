"""Helper utilities for notebooks"""

from datetime import datetime
from json import dumps, loads

import pandas as pd
from bs4 import BeautifulSoup


def pprint_json(jstr):
    """Pretty print JSON.

    Parameters
    ----------
    jstr : str
        JSON string to pretty print.
    """
    print(dumps(loads(jstr), indent=2))


def clean_html(html_text):
    """Remove HTML tags and return clean text.

    Parameters
    ----------
    html_text : str
        HTML text to clean. Can be NaN.

    Returns
    -------
    str
        Clean text with HTML tags removed. Returns empty string if input
        is NaN.
    """
    if pd.isna(html_text):
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def display_dataframe(df):
    """Display dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to display.

    Notes
    -----
    Prints the first few rows and column names of the dataframe.
    """
    print(df.head())
    print(df.columns)


def format_date(iso_date_string: str) -> str:
    """Convert ISO 8601 datetime string to readable format.

    Parameters
    ----------
    iso_date_string : str
        ISO 8601 formatted datetime string (e.g., "2025-11-22T18:11:23.522Z").

    Returns
    -------
    str
        Human-readable date string in YYYY-MM-DD HH:MM format
        (e.g., "2025-11-22 18:11").

    Examples
    --------
    >>> format_date("2025-11-22T18:11:23.522Z")
    '2025-11-22 18:11'
    """
    # Handle UTC timezone indicator
    date_str = iso_date_string.replace("Z", "+00:00")
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%Y-%m-%d %H:%M")
