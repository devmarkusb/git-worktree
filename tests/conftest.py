"""Load the extensionless `git-worktree` script as a normal module for tests."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "git-worktree"


def load_git_worktree():
    # spec_from_file_location returns None for extensionless paths on some Python
    # versions; SourceFileLoader handles the real script path reliably.
    path = str(SCRIPT_PATH)
    loader = SourceFileLoader("git_worktree_under_test", path)
    spec = importlib.util.spec_from_loader(loader.name, loader, origin=path)
    if spec is None:
        raise RuntimeError(f"Could not build spec for {SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gw():
    """The git-worktree script loaded as `git_worktree_under_test`."""
    return load_git_worktree()
