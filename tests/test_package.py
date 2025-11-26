from __future__ import annotations

import importlib.metadata

import nutshell as m


def test_version():
    """Test that the version matches."""
    assert importlib.metadata.version("nutshell") == m.__version__
