from __future__ import annotations

from pathlib import Path

import pytest


def test_resolve_git_sub_from_env(gw, tmp_path: Path, monkeypatch):
    sub = tmp_path / "custom-git-sub"
    sub.write_text("#!/bin/sh\necho ok\n")
    sub.chmod(0o755)
    monkeypatch.setenv("GIT_SUB", str(sub))
    monkeypatch.delenv("PATH", raising=False)
    found = gw.resolve_git_sub(tmp_path / "dummy" / "git-worktree")
    assert found == sub.resolve()


def test_resolve_git_sub_env_missing_file_dies(gw, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GIT_SUB", str(tmp_path / "does-not-exist"))
    with pytest.raises(SystemExit):
        gw.resolve_git_sub(tmp_path / "git-worktree")


def test_resolve_git_sub_which(gw, tmp_path: Path, monkeypatch):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    sub = bindir / "git-sub"
    sub.write_text("#!/bin/sh\necho ok\n")
    sub.chmod(0o755)
    monkeypatch.delenv("GIT_SUB", raising=False)
    monkeypatch.setenv("PATH", str(bindir))
    found = gw.resolve_git_sub(tmp_path / "somewhere" / "git-worktree")
    assert found == sub.resolve()


def test_resolve_git_sub_sibling(gw, tmp_path: Path, monkeypatch):
    monkeypatch.delenv("GIT_SUB", raising=False)
    monkeypatch.setenv("PATH", "")
    parent = tmp_path / "parent"
    (parent / "git-worktree").mkdir(parents=True)
    script = parent / "git-worktree" / "git-worktree"
    script.write_text("#\n")
    sibling = parent / "git-sub" / "git-sub"
    sibling.parent.mkdir(parents=True)
    sibling.write_text("#\n")
    found = gw.resolve_git_sub(script)
    assert found == sibling.resolve()


def test_resolve_git_sub_none(gw, tmp_path: Path, monkeypatch):
    monkeypatch.delenv("GIT_SUB", raising=False)
    monkeypatch.setenv("PATH", "")
    parent = tmp_path / "solo"
    (parent / "git-worktree").mkdir(parents=True)
    script = parent / "git-worktree" / "git-worktree"
    script.write_text("#\n")
    assert gw.resolve_git_sub(script) is None
