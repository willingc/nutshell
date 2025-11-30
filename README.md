# discuss-nutshell

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/willingc/discuss-nutshell/workflows/CI/badge.svg
[actions-link]:             https://github.com/willingc/discuss-nutshell/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/discuss-nutshell
[conda-link]:               https://github.com/conda-forge/discuss-nutshell-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/willingc/discuss-nutshell/discussions
[pypi-link]:                https://pypi.org/project/discuss-nutshell/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/discuss-nutshell
[pypi-version]:             https://img.shields.io/pypi/v/discuss-nutshell
[rtd-badge]:                https://readthedocs.org/projects/discuss-nutshell/badge/?version=latest
[rtd-link]:                 https://discuss-nutshell.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->

Improve your understanding of long Discourse threads.

## Problem statement

Discourse topics, such as on discuss.python.org, can get very long even over a
few hours or days. These long threads makes it difficult to understand the
conversation without spending one to three hours reading the thread. Discourse
gives a predicted time to read the thread.

On discuss.python.org, discussion threads about an individual
[Python Enhancement Proposal](https://peps.python.org) (PEP), can get very long.
To understand the pros and cons of the PEP, reading the thread is needed.

## Motivation

I want a time-efficient way to read posts and summarize the key points. Ideally,
I would like to understand the pros and cons of an individual PEPs.
Understanding the authors' motivations and their background also is important.

Recapping the conversation in an accurate way would be very helpful.

## Initial approach

Take a Discourse topic and parse it into posts that can be queried.

- `data_loader.py`: Hit an endpoint and save to json
- `preprocessor.py`: Do data cleaning and parsing into individual post files
- `launch_app.py`: Launch gradio app to interact with the LLM and log queries,
  context, responses

Take the db file and use datasette to view: `datasette data/posts_qa_logs.db`

Summarize individual posts and aggregate the summarized posts into one posts
file that can be queried.

Use a simple Gradio UI to interface with the user.

## Next phases

Data to keep: Authors, date/time, post number, uuid post, core dev (bool),
cooked message, summarized message

Possible prompts

- Does this message support or refute the proposed PEP?
- What are key topics found in the message
- How many times has a person posted
- You are a Python expert. Summarize this message.
- You are an intermediate Python user. Summarize this message.
- You are a manager not a developer. Summarize this message.

Report on pros and cons of the PEP proposal.

Query in 10 message chunks and summarize.

- Create a visual display of individual posts, summaries, author, and date
  posted.
- Display the summaries but allow the original post text to be accessed easily.
- Plot a sentiment of messages over time.
