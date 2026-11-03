# Agent Instructions

## Project overview

`git-worktree` is a standalone, dependency-free Python 3.8+ executable. It creates linked Git
worktrees with predictable directory names, runs optional `git-sub` setup after adding a worktree,
recreates selected external configuration symlinks, and lists or forcibly removes managed worktrees.

## Development and checks

- No package build is needed; `pyproject.toml` contains tool configuration.
- Use Python 3.10+ for the full development toolchain. Create and activate a virtual environment,
  then run `pip install -r requirements-dev.txt`.
- Run hook setup from this repository's root: `pre-commit install`. A parent repository containing
  this checkout as a submodule has separate hooks and configuration.
- For an existing `.githooks` installation, remove its local override before installing the standard
  hook: `git config --local --unset-all core.hooksPath`.
- Format Markdown: `pre-commit run mdformat --all-files --show-diff-on-failure`.
- Lint: `ruff check git-worktree tests`.
- Test: `pytest tests/ --cov=. --cov-config=pyproject.toml --cov-report=term-missing`.
- CI tests Linux and macOS on Python 3.8, 3.10, and 3.12, plus Linux on 3.13. The Markdown hook runs
  on Python 3.10+; Python 3.8 installs the remaining development requirements.

## Architecture

- `git-worktree`: argument parsing, Git subprocess operations, managed-path naming, companion
  resolution, and external-symlink discovery/recreation.
- Companion resolution: `GIT_SUB`, then `git-sub` on PATH, then a sibling checkout, then a built-in
  recursive submodule initialization fallback.
- `tests/`: pure and mocked subprocess tests plus integration tests using temporary Git
  repositories. `tests/conftest.py` imports the extensionless executable with `SourceFileLoader`.
- `.pre-commit-config.yaml`: official mdformat hook with pinned GFM support. `.mdformat.toml` holds
  the 100-column formatting policy. Keep Markdown parsing and hook execution in the upstream tools.
- `.github/workflows/ci.yml`: lint, formatting, tests, coverage, and optional Codecov upload.

## Conventions and testing

- Preserve Python 3.8 runtime compatibility, stdlib-only runtime imports, and executable file mode.
- Follow the Ruff rules and 100-character line length configured in `pyproject.toml`.
- Cover behavior changes with focused tests. Use mocks for isolated subprocess behavior and
  temporary repositories with local Git identity for integration tests; avoid the user's real
  worktrees.
- Symlink tests must account for platform permissions. Preserve existing platform-specific skips.
- The standard pre-commit hook formats staged Markdown and temporarily saves unstaged changes. If it
  edits files, review and stage the formatted result, then retry the commit.

## Scope and safety

- Keep changes inside this checkout; it may be a submodule of another repository. Review status and
  diffs here, and report which checks actually ran.
- Runtime `add` creates directories/branches and can execute the selected `git-sub` companion.
  Runtime `remove` invokes `git worktree remove -f` and can discard local work. Run mutations only
  when requested and against the intended repository/worktree.
- Symlinks can point to personal configuration outside the repository. Leave those targets
  untouched.
- Preserve the existing companion selection behavior; rely on Git and optional `git-sub` already
  available rather than installing system tools or escalating privileges.
- Keep secrets, local environments, generated caches, and coverage output out of commits. Changes to
  CI, dependency configuration, or release tooling should serve the requested task.
- Pushes and other publishing actions require explicit user authorization.
