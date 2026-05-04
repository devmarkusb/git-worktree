from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "git-worktree"


def test_worktree_path(gw):
    root = Path("/tmp/proj/myrepo")
    assert gw.worktree_path(root, "main") == Path("/tmp/proj/myrepo-main")
    assert gw.worktree_path(root, "feature/foo") == Path("/tmp/proj/myrepo-feature-foo")


def test_parse_argv_add(gw):
    assert gw.parse_argv(["x"]) == ("add", "x")
    assert gw.parse_argv(["my-branch"]) == ("add", "my-branch")


def test_parse_argv_remove(gw):
    assert gw.parse_argv(["remove", "x"]) == ("remove", "x")
    assert gw.parse_argv(["rm", "feature-a"]) == ("remove", "feature-a")


def test_parse_argv_help(gw):
    with pytest.raises(SystemExit) as ei:
        gw.parse_argv(["--help"])
    assert ei.value.code == 0


def test_parse_argv_help_short(gw):
    with pytest.raises(SystemExit) as ei:
        gw.parse_argv(["-h"])
    assert ei.value.code == 0


def test_parse_argv_errors(gw):
    with pytest.raises(SystemExit):
        gw.parse_argv([])
    with pytest.raises(SystemExit):
        gw.parse_argv(["remove"])
    with pytest.raises(SystemExit):
        gw.parse_argv(["remove", "a", "b"])
    with pytest.raises(SystemExit):
        gw.parse_argv(["rm", "  "])


def test_is_python_script_py_suffix(gw, tmp_path: Path):
    p = tmp_path / "x.py"
    p.write_text("# not shebang\n")
    assert gw.is_python_script(p) is True


def test_is_python_script_shebang_python(gw, tmp_path: Path):
    p = tmp_path / "tool"
    p.write_bytes(b"#!/usr/bin/env python3\nprint(1)\n")
    assert gw.is_python_script(p) is True


def test_is_python_script_shebang_not_python(gw, tmp_path: Path):
    p = tmp_path / "tool"
    p.write_bytes(b"#!/bin/sh\necho hi\n")
    assert gw.is_python_script(p) is False


def test_is_python_script_missing(gw, tmp_path: Path):
    p = tmp_path / "nope"
    assert gw.is_python_script(p) is False


def test_main_help_exits_zero():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "worktree" in r.stdout.lower()


def test_main_usage_exits_nonzero():
    r = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
