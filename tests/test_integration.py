from __future__ import annotations

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
    branch = "feature-wt"
    wt_path = git_repo.parent / f"{git_repo.name}-{branch}"

    r = subprocess.run(
        [sys.executable, str(SCRIPT), branch],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert wt_path.is_dir()
    assert (wt_path / "README.md").read_text() == "# hi\n"

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
        [sys.executable, str(SCRIPT), branch],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    assert "already exists" in (r.stderr + r.stdout).lower() or "exists" in (r.stderr + r.stdout)
