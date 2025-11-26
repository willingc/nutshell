from __future__ import annotations

import shutil
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()
PROJECT = nox.project.load_toml()

nox.needs_version = ">=2025.2.9"
nox.options.default_venv_backend = "uv|virtualenv"


@nox.session
def lint(session: nox.Session) -> None:
    """Run the linter."""
    session.install("pre-commit")
    session.run(
        "python",
        "-m",
        "pre_commit",
        "run",
        "--all-files",
        "--show-diff-on-failure",
        *session.posargs,
    )


@nox.session
def pylint(session: nox.Session) -> None:
    """Run Pylint."""
    # This needs to be installed into the package environment, and is slower
    # than a pre-commit check
    session.install("-e.", "pylint>=3.2")
    # Only fail on errors, not warnings
    session.run(
        "python",
        "-m",
        "pylint",
        "--fail-under=0",
        "src/nutshell",
        *session.posargs,
    )


@nox.session
def tests(session: nox.Session) -> None:
    """Run the unit and regular tests."""
    test_deps = nox.project.dependency_groups(PROJECT, "test")
    session.install("-e.", *test_deps)
    session.run("python", "-m", "pytest", *session.posargs)


@nox.session(reuse_venv=True, default=False)
def docs(session: nox.Session) -> None:
    """Make or serve the docs. Pass --non-interactive to avoid serving."""
    doc_deps = nox.project.dependency_groups(PROJECT, "docs")
    session.install("-e.", *doc_deps)

    if session.interactive:
        session.run("python", "-m", "mkdocs", "serve", "--clean", *session.posargs)
    else:
        session.run("python", "-m", "mkdocs", "build", "--clean", *session.posargs)


@nox.session(default=False)
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """

    build_path = DIR.joinpath("build")
    if build_path.exists():
        shutil.rmtree(build_path)

    session.install("build")
    session.run("python", "-m", "build")
