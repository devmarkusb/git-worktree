# git-worktree

**Linked Git worktrees with a predictable path—and teardown that still works when submodules get in the way.**

Single Python file. After each **add** it runs **git-sub** when available (full submodule + optional LFS), otherwise a **minimal built-in** `git submodule update --init --recursive`. **Remove** uses `git worktree remove -f` so dirty trees and submodule checkouts do not block cleanup.

## Requirements

- Python 3.8+ (uses postponed annotations)
- `git` on your PATH (Git for Windows is enough on Windows)

## Install

The script is stored in Git as **executable** (`100755`), so on macOS/Linux a fresh clone is usually runnable as `./git-worktree` without `chmod`. If your checkout lost `+x` (e.g. `core.filemode false`, odd FS), run `chmod +x git-worktree` once.

```bash
cp git-worktree ~/bin/   # or symlink; keep one directory on your PATH
```

On Windows:

```text
python C:\path\to\git-worktree my-branch
```

## Companion: [git-sub](https://github.com/devmarkusb/git-sub) (optional but recommended)

> **Separate project.** Use **[git-sub](https://github.com/devmarkusb/git-sub)** if you want **submodules + Git LFS** in one step after each worktree add (same style as this repo: one Python file). Skip this section if you only need the built-in submodule fallback.

`git-worktree` picks a `git-sub` in this order — **no pip required**:

1. **`GIT_SUB`** — absolute path to the `git-sub` file, if you keep it somewhere custom.
2. **`git-sub` on your PATH** — e.g. copy both scripts into `~/bin`.
3. **Sibling clone** — clone both repos under the same parent with the default names:
   - `…/git-worktree/git-worktree`
   - `…/git-sub/git-sub`  
   Then run this script from the `git-worktree` checkout; it finds the sibling automatically.
4. **Built-in fallback** — submodule init only (no LFS pull).

## Usage

```text
git-worktree <branch>           # create worktree + post-add hook (see above)
git-worktree remove|rm <branch> # remove (forced: safe with submodules / local changes)
git-worktree --help
```

The worktree directory is always:

`<parent-of-repo>/<repo-dir-name>-<branch with / turned into ->`

On **remove**, pass the **same `<branch>` string you used when creating** the worktree (it encodes the folder name), not necessarily the branch currently checked out there.

## License

MIT — see [LICENSE](LICENSE).
