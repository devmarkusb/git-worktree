# git-worktree

[![CI](https://github.com/devmarkusb/git-worktree/actions/workflows/ci.yml/badge.svg)](https://github.com/devmarkusb/git-worktree/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.8%2B-informational)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Codecov](https://codecov.io/gh/devmarkusb/git-worktree/graph/badge.svg)](https://codecov.io/gh/devmarkusb/git-worktree)

**Linked Git worktrees with a predictable path—and teardown that still works when submodules get in
the way.**

Single Python file. After each **add** it runs **git-sub** when available (full submodule + optional
LFS), otherwise a **minimal built-in** `git submodule update --init --recursive`. **Remove** uses
`git worktree remove -f` so dirty trees and submodule checkouts do not block cleanup.

After each **add** it also recreates symlinks that resolve outside the repository when the same link
is present in the source worktree and at least one other existing worktree. This is meant for
ignored personal config such as `CMakeUserPresets.json`, `.run`, or `.idea/runConfigurations`.
Common generated directories such as `venv`, `.venv`, `node_modules`, and `cmake-build-*` are pruned
while scanning. For the first added worktree, where no second worktree exists yet, it bootstraps
from ignored external symlinks in the source worktree and skips obvious system targets.

## Requirements

- Python 3.8+ (uses postponed annotations)
- `git` on your PATH (Git for Windows is enough on Windows)

## Development

The full development toolchain requires Python 3.10+; the standalone script still runs on Python
3.8+. Run setup from the root of the `git-worktree` checkout. If it is a submodule, enter its
directory first: `pre-commit install` installs hooks in the current repository, and a parent
repository has separate hook configuration.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pre-commit install
pre-commit run mdformat --all-files
ruff check git-worktree tests
pytest tests/ --cov=. --cov-config=pyproject.toml --cov-report=term-missing
```

If you previously enabled `.githooks`, run `git config --local --unset-all core.hooksPath` before
`pre-commit install`.

The standard pre-commit hook automatically formats staged Markdown with mdformat and GitHub Flavored
Markdown support. It uses the 100-column policy in `.mdformat.toml`; formatter versions are pinned
in `.pre-commit-config.yaml`. Pre-commit manages its own formatter environment and temporarily saves
unstaged changes while running. If formatting changes a file, the commit pauses: review and stage
the formatted result, then retry the commit. To format one file, run
`pre-commit run mdformat --files README.md`.

Agent guidance lives in `AGENTS.md`; `CLAUDE.md` and `GEMINI.md` point to it.

CI runs on pushes and pull requests to `main` (Linux and macOS, multiple Python versions). Optional
[Codecov](https://codecov.io/gh/devmarkusb/git-worktree) uploads use the `CODECOV_TOKEN` repository
secret when set. The Markdown hook runs on Python 3.10+; Python 3.8 installs only the compatible
requirements and runs lint and tests.

## Install

The script is stored in Git as **executable** (`100755`), so on macOS/Linux a fresh clone is usually
runnable as `./git-worktree` without `chmod`. If your checkout lost `+x` (e.g.
`core.filemode false`, odd FS), run `chmod +x git-worktree` once.

```bash
cp git-worktree ~/bin/   # or symlink; keep one directory on your PATH
```

On Windows:

```text
python C:\path\to\git-worktree add my-branch
```

## Companion: [git-sub](https://github.com/devmarkusb/git-sub) (optional but recommended)

> **Separate project.** Use **[git-sub](https://github.com/devmarkusb/git-sub)** if you want
> **submodules + Git LFS** in one step after each worktree add (same style as this repo: one Python
> file). Skip this section if you only need the built-in submodule fallback.

`git-worktree` picks a `git-sub` in this order — **no pip required**:

1. **`GIT_SUB`** — absolute path to the `git-sub` file, if you keep it somewhere custom.

2. **`git-sub` on your PATH** — e.g. copy or link both scripts into `~/bin`.

3. **Sibling clone** — clone both repos under the same parent with the default names:

   - `…/git-worktree/git-worktree`
   - `…/git-sub/git-sub`

   Then run this script from the `git-worktree` checkout; it finds the sibling automatically.

4. **Built-in fallback** — submodule init only (no LFS pull).

## Usage

```text
git-worktree add <branch>       # create worktree + post-add hook (see above)
git-worktree list|ls            # list worktrees; prints rm <name> hints after
git-worktree remove|rm <branch> # remove (forced: safe with submodules / local changes)
git-worktree --help
```

The worktree directory is always:

`<parent-of-repo>/<repo-dir-name>-<branch with / turned into ->`

On **remove**, pass that folder suffix (what `ls` lists after the git output), not necessarily the
branch currently checked out there. Paths outside this naming scheme are listed as not managed —
remove those with `git worktree remove -f <path>`.

## License

MIT — see [LICENSE](LICENSE).
