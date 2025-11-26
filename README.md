# nutshell

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/willingc/discourse-to-sqlite/workflows/CI/badge.svg
[actions-link]:             https://github.com/willingc/discourse-to-sqlite/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/discourse-to-sqlite
[conda-link]:               https://github.com/conda-forge/discourse-to-sqlite-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/willingc/discourse-to-sqlite/discussions
[pypi-link]:                https://pypi.org/project/discourse-to-sqlite/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/discourse-to-sqlite
[pypi-version]:             https://img.shields.io/pypi/v/discourse-to-sqlite
[rtd-badge]:                https://readthedocs.org/projects/discourse-to-sqlite/badge/?version=latest
[rtd-link]:                 https://discourse-to-sqlite.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->

Take a Discourse topic and parse it into posts that can be queried.

- `data_loader.py`: Hit an endpoint and save to json
- `preprocessor.py`: Do data cleaning and parsing into individual post files
- `launch_app.py`: Launch gradio app to interact with the LLM and log queries,
  context, responses

Take the db file and use datasette to view: `datasette data/posts_qa_logs.db`

## Next phase

Authors, date/time, post number, uuid post, core dev (bool), cooked message,
summarized message

- Does this message support or refute the PEP?
- What are key topics found in the message
- How many times has a person posted

Summarize the thread.

Report on pros and cons of the PEP proposal.

- Embeddings
- Vector database like chroma
- chunks

Query with chunks and prompt
