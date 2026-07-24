from __future__ import annotations

import os
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


def test_managed_remove_name(gw, tmp_path: Path):
    root = tmp_path / "myrepo"
    root.mkdir()
    assert gw.managed_remove_name(root, root) is None
    assert gw.managed_remove_name(root, tmp_path / "myrepo-sidequest") == "sidequest"
    assert gw.managed_remove_name(root, tmp_path / "myrepo-feature-foo") == "feature-foo"
    assert gw.managed_remove_name(root, tmp_path / "other-sidequest") is None
    assert gw.managed_remove_name(root, Path("/tmp/myrepo-sidequest")) is None


def test_print_rm_hint_lists_unmanaged(gw, tmp_path: Path, capsys):
    root = tmp_path / "myrepo"
    root.mkdir()
    managed = tmp_path / "myrepo-sidequest"
    managed.mkdir()
    foreign = tmp_path / "scratch"
    foreign.mkdir()
    gw.print_rm_hint(root, [root, managed, foreign])
    out = capsys.readouterr().out
    assert "rm sidequest" in out
    assert "not managed" in out
    assert str(foreign) in out
    assert "(none)" not in out


def test_print_rm_hint_unmanaged_none(gw, tmp_path: Path, capsys):
    root = tmp_path / "myrepo"
    root.mkdir()
    managed = tmp_path / "myrepo-sidequest"
    managed.mkdir()
    gw.print_rm_hint(root, [root, managed])
    out = capsys.readouterr().out
    assert "not managed" in out
    assert "(none)" in out


def test_cmd_list_uses_main_worktree_for_remove_hints_from_linked_worktree(
    gw, monkeypatch, capsys
):
    main = Path("/repos/project")
    linked = Path("/repos/project-feature")
    monkeypatch.setattr(gw, "repo_root", lambda: linked)
    monkeypatch.setattr(gw, "git_worktree_roots", lambda: [main, linked])
    monkeypatch.setattr(gw, "git_run", lambda args: None)

    gw.cmd_list()

    out = capsys.readouterr().out
    assert "rm feature" in out
    assert "/repos/project" not in out


def test_cmd_remove_uses_main_worktree_from_linked_worktree(gw, monkeypatch):
    main = Path("/repos/project")
    linked = Path("/repos/project-feature")
    calls = []
    monkeypatch.setattr(gw, "repo_root", lambda: linked)
    monkeypatch.setattr(gw, "git_worktree_roots", lambda: [main, linked])
    monkeypatch.setattr(gw, "git_run", lambda args: calls.append(args))

    gw.cmd_remove("feature")

    assert calls == [["worktree", "remove", "-f", str(linked)]]


def test_parse_argv_add(gw):
    assert gw.parse_argv(["add", "x"]) == ("add", "x")
    assert gw.parse_argv(["add", "list"]) == ("add", "list")


def test_parse_argv_remove(gw):
    assert gw.parse_argv(["remove", "x"]) == ("remove", "x")
    assert gw.parse_argv(["rm", "feature-a"]) == ("remove", "feature-a")


def test_parse_argv_list(gw):
    assert gw.parse_argv(["list"]) == ("list", None)
    assert gw.parse_argv(["ls"]) == ("list", None)


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
        gw.parse_argv(["list", "extra"])
    with pytest.raises(SystemExit):
        gw.parse_argv(["add"])
    with pytest.raises(SystemExit):
        gw.parse_argv(["add", "a", "b"])
    with pytest.raises(SystemExit):
        gw.parse_argv(["bla"])
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


@pytest.mark.skipif(os.name == "nt", reason="symlink creation needs privileges on Windows")
def test_find_external_symlinks_skips_internal_and_generated_dirs(gw, tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / "config.json").write_text("{}\n")
    (root / "internal").write_text("repo\n")
    os.symlink("internal", root / "internal-link")
    os.symlink(shared / "config.json", root / "CMakeUserPresets.json")

    idea = root / ".idea"
    idea.mkdir()
    os.symlink(shared, idea / "runConfigurations")

    venv_bin = root / "venv" / "bin"
    venv_bin.mkdir(parents=True)
    os.symlink(sys.executable, venv_bin / "python")

    found = gw.find_external_symlinks(root)
    assert [link.relpath.as_posix() for link in found] == [
        ".idea/runConfigurations",
        "CMakeUserPresets.json",
    ]


@pytest.mark.skipif(os.name == "nt", reason="symlink creation needs privileges on Windows")
def test_recreate_external_symlinks_preserves_targets(gw, tmp_path: Path):
    source = tmp_path / "source" / "repo"
    sibling = tmp_path / "sibling" / "repo-other"
    target = tmp_path / "target" / "repo-branch"
    source.mkdir(parents=True)
    sibling.mkdir(parents=True)
    target.mkdir(parents=True)
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / "preset.json").write_text("{}\n")

    os.symlink(shared / "preset.json", source / "CMakeUserPresets.json")
    os.symlink("../../shared", source / "relative-shared")
    os.symlink(shared / "preset.json", sibling / "CMakeUserPresets.json")
    os.symlink("../../shared", sibling / "relative-shared")
    os.symlink(sys.executable, source / "source-only")

    created = gw.recreate_external_symlinks(source, [source, sibling], target)
    assert [path.as_posix() for path in created] == [
        "CMakeUserPresets.json",
        "relative-shared",
    ]
    assert (target / "CMakeUserPresets.json").is_symlink()
    assert (target / "CMakeUserPresets.json").resolve() == shared / "preset.json"
    assert (target / "relative-shared").is_symlink()
    assert (target / "relative-shared").resolve() == shared
    assert not (target / "source-only").exists()


@pytest.mark.skipif(os.name == "nt", reason="symlink creation needs privileges on Windows")
def test_recreate_external_symlinks_requires_shared_link(gw, tmp_path: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    shared = tmp_path / "shared"
    source.mkdir()
    target.mkdir()
    shared.mkdir()
    os.symlink(shared, source / ".run")

    created = gw.recreate_external_symlinks(source, [source], target)
    assert created == []
    assert not (target / ".run").exists()


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
