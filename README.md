# git-worktree

**Linked Git worktrees with a predictable path—and teardown that still works when submodules get in the way.**

One Python file (`git-worktree`) plus a tiny optional `git-sub` hook: after each **add**, submodules are initialized in the new tree; **remove** uses `git worktree remove -f` so dirty trees and submodule checkouts do not block cleanup.

## Requirements

- Python 3.8+ (uses postponed annotations)
- `git` on your PATH

## Install

From a clone:

```bash
chmod +x git-worktree git-sub
cp git-worktree git-sub ~/bin/   # or another directory on your PATH
```

On Windows, run with Python explicitly, for example:

```text
python C:\path\to\git-worktree my-branch
```

Put both files in the same folder if you rely on the bundled `git-sub`.

## Usage

```text
git-worktree <branch>           # create worktree + run git-sub
git-worktree remove|rm <branch> # remove (forced: safe with submodules / local changes)
git-worktree --help
```

The worktree directory is always:

`<parent-of-repo>/<repo-dir-name>-<branch with / turned into ->`

On **remove**, pass the **same `<branch>` string you used when creating** the worktree (it encodes the folder name), not necessarily the branch currently checked out there.

## `git-sub`

- If `git-sub` exists on your **PATH**, that executable is used (handy for a richer script from your dotfiles).
- Otherwise the **bundled** `git-sub` next to `git-worktree` runs (`git submodule update --init --recursive`).
- Replace the bundled file, or shadow it via PATH, if you need LFS, shallow clones, etc.

## License

MIT — see [LICENSE](LICENSE).
