# git-worktree

**Linked Git worktrees with a predictable path—and teardown that still works when submodules get in the way.**

Single Python file: after each **add** it runs `git submodule update --init --recursive` in the new tree (same `git` on your PATH—works on Windows). **Remove** uses `git worktree remove -f` so dirty trees and submodule checkouts do not block cleanup.

## Requirements

- Python 3.8+ (uses postponed annotations)
- `git` on your PATH (Git for Windows is enough on Windows)

## Install

```bash
chmod +x git-worktree
cp git-worktree ~/bin/   # or another directory on your PATH
```

On Windows:

```text
python C:\path\to\git-worktree my-branch
```

## Usage

```text
git-worktree <branch>           # create worktree + submodule init
git-worktree remove|rm <branch> # remove (forced: safe with submodules / local changes)
git-worktree --help
```

The worktree directory is always:

`<parent-of-repo>/<repo-dir-name>-<branch with / turned into ->`

On **remove**, pass the **same `<branch>` string you used when creating** the worktree (it encodes the folder name), not necessarily the branch currently checked out there.

## Git LFS

This tool only runs `git submodule update --init --recursive`. If your repo uses **Git LFS**, run `git lfs pull` (or your usual LFS step) inside the new worktree after creation.

## License

MIT — see [LICENSE](LICENSE).
