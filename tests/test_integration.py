from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "git-worktree"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "myrepo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("# hi\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")
    return repo


def test_add_and_remove_worktree(git_repo: Path):
    branch = "list"
    wt_path = git_repo.parent / f"{git_repo.name}-{branch}"

    r = subprocess.run(
        [sys.executable, str(SCRIPT), "add", branch],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert wt_path.is_dir()
    assert (wt_path / "README.md").read_text() == "# hi\n"

    r_list = subprocess.run(
        [sys.executable, str(SCRIPT), "list"],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r_list.returncode == 0, r_list.stderr + r_list.stdout
    assert str(git_repo) in r_list.stdout
    assert str(wt_path) in r_list.stdout
    assert f"rm {branch}" in r_list.stdout
    assert "folder suffix" in r_list.stdout

    r_bad = subprocess.run(
        [sys.executable, str(SCRIPT), "rm", "does-not-exist"],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r_bad.returncode != 0
    err = r_bad.stderr + r_bad.stdout
    assert "no managed worktree" in err
    assert f"rm {branch}" in err

    r2 = subprocess.run(
        [sys.executable, str(SCRIPT), "rm", branch],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r2.returncode == 0, r2.stderr + r2.stdout
    assert not wt_path.exists()


def test_add_refuses_existing_path(git_repo: Path):
    branch = "blocked"
    wt_path = git_repo.parent / f"{git_repo.name}-{branch}"
    wt_path.mkdir()
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "add", branch],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    assert "already exists" in (r.stderr + r.stdout).lower() or "exists" in (r.stderr + r.stdout)


@pytest.mark.skipif(os.name == "nt", reason="symlink creation needs privileges on Windows")
def test_add_bootstraps_ignored_external_symlinks_for_first_worktree(
    git_repo: Path,
    tmp_path: Path,
):
    branch = "first-links"
    wt_path = git_repo.parent / f"{git_repo.name}-{branch}"
    shared = tmp_path / "shared-config"
    shared.mkdir()
    (shared / "CMakeUserPresets.json").write_text("{}\n")

    (git_repo / ".gitignore").write_text("CMakeUserPresets.json\n.run\nvenv/\n")
    os.symlink(shared / "CMakeUserPresets.json", git_repo / "CMakeUserPresets.json")
    os.symlink(shared, git_repo / ".run")
    os.symlink(shared, git_repo / "not-ignored")

    venv_bin = git_repo / "venv" / "bin"
    venv_bin.mkdir(parents=True)
    os.symlink(sys.executable, venv_bin / "python")

    r = subprocess.run(
        [sys.executable, str(SCRIPT), "add", branch],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert (wt_path / "CMakeUserPresets.json").is_symlink()
    assert (wt_path / "CMakeUserPresets.json").resolve() == shared / "CMakeUserPresets.json"
    assert (wt_path / ".run").is_symlink()
    assert (wt_path / ".run").resolve() == shared
    assert not (wt_path / "not-ignored").exists()
    assert not (wt_path / "venv" / "bin" / "python").exists()


@pytest.mark.skipif(os.name == "nt", reason="symlink creation needs privileges on Windows")
def test_add_recreates_external_symlinks(git_repo: Path, tmp_path: Path):
    branch = "with-links"
    existing_branch = "already-linked"
    existing_path = git_repo.parent / f"{git_repo.name}-{existing_branch}"
    wt_path = git_repo.parent / f"{git_repo.name}-{branch}"
    shared = tmp_path / "shared-config"
    run_configs = shared / ".idea" / "runConfigurations"
    run_configs.mkdir(parents=True)
    (shared / "CMakeUserPresets.json").write_text("{}\n")
    (run_configs / "demo.xml").write_text("<component />\n")

    os.symlink(shared / "CMakeUserPresets.json", git_repo / "CMakeUserPresets.json")
    (git_repo / ".idea").mkdir()
    os.symlink(run_configs, git_repo / ".idea" / "runConfigurations")

    _git(git_repo, "worktree", "add", "-b", existing_branch, str(existing_path))
    os.symlink(shared / "CMakeUserPresets.json", existing_path / "CMakeUserPresets.json")
    (existing_path / ".idea").mkdir()
    os.symlink(run_configs, existing_path / ".idea" / "runConfigurations")

    venv_bin = git_repo / "venv" / "bin"
    venv_bin.mkdir(parents=True)
    os.symlink(sys.executable, venv_bin / "python")

    r = subprocess.run(
        [sys.executable, str(SCRIPT), "add", branch],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert (wt_path / "CMakeUserPresets.json").is_symlink()
    assert (wt_path / "CMakeUserPresets.json").resolve() == shared / "CMakeUserPresets.json"
    assert (wt_path / ".idea" / "runConfigurations").is_symlink()
    assert (wt_path / ".idea" / "runConfigurations").resolve() == run_configs
    assert not (wt_path / "venv" / "bin" / "python").exists()
    assert "Recreated external symlinks" in r.stdout
