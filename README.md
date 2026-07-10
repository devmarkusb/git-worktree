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

```bash
git config core.hooksPath .githooks
pip install 'pytest>=7.4' 'pytest-cov>=4.1' 'ruff>=0.4'
python3 tools/format_markdown.py README.md
python3 tools/format_markdown.py --check --tracked
ruff check git-worktree tests tools/format_markdown.py
pytest tests/ --cov=. --cov-config=pyproject.toml --cov-report=term-missing
```

The hook formats staged Markdown files to 100 columns before each commit and re-stages files it
changes.

CI runs on pushes and pull requests to `main` (Linux and macOS, multiple Python versions). Optional
[Codecov](https://codecov.io/gh/devmarkusb/git-worktree) uploads use the `CODECOV_TOKEN` repository
secret when set.

## Install

The script is stored in Git as **executable** (`100755`), so on macOS/Linux a fresh clone is usually
runnable as `./git-worktree` without `chmod`. If your checkout lost `+x` (e.g. `core.filemode
false`, odd FS), run `chmod +x git-worktree` once.

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
git-worktree list|ls            # list linked worktrees
git-worktree remove|rm <branch> # remove (forced: safe with submodules / local changes)
git-worktree --help
```

The worktree directory is always:

`<parent-of-repo>/<repo-dir-name>-<branch with / turned into ->`

On **remove**, pass the **same `<branch>` string you used when creating** the worktree (it encodes
the folder name), not necessarily the branch currently checked out there.

## License

MIT — see [LICENSE](LICENSE).
