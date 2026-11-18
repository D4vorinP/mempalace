# feature/wing-routes

Fork of MemPalace (one commit on top of upstream `develop`) so the Claude Code hooks file every
worktree of a project into one wing. Upstream tracks the same problem as MemPalace/mempalace#2939;
this branch builds its first two proposals for own use only, with no upstream PR or comment (decided
by the user).

## 2026-11-18 — Root detection and wing_routes for hook ingest

### Done
- `_project_wing` and `_wing_from_jsonl_cwd` now resolve a session's cwd to the repository root before
  naming the wing: a linked worktree resolves to its main clone, a subdirectory to its repository, a
  submodule stays itself, a folder that no longer exists stays as it is.
- New `wing_routes` config (`[{"path": glob, "wing": name}]`, `{name}` = matched folder) applied to the
  resolved root before the leaf-name and workstation fallbacks; first match wins.
- `_repo_common_dir` moved from `miner.py` to a new light `gitdir.py`, which both import.
- 11 new tests (real git clone plus sibling worktree, routes, precedence, malformed config). Hook,
  config and miner test files: 627 passed, 4 skipped; ruff clean.
- Checked against this machine's real transcripts with the planned routes: three deleted
  `BlueTrader-New-*` worktrees, the main clone and the home folder all resolve to the intended wings.
- Forked to `D4vorinP/mempalace` and pushed this branch there; the `upstream` remote's push URL is
  disabled so nothing reaches MemPalace by accident.
- Moved from `v3.12.0` onto upstream `develop` (12 unreleased commits, none touching the changed files)
  and squashed into one commit. Full suite on the result: 8,102 passed, 573 skipped, 0 failed.
- `~/.claude/scripts/install-mempalace.ps1`, modelled on `install-dotnet-mcp.ps1`: a plain run fetches
  and installs the fork as the `mempalace` uv tool with `[dml]`; `-SyncUpstream` rebases onto upstream
  `develop`, runs the hook, config and miner tests and force-pushes with lease. It refuses to install
  while any MemPalace process runs. A once-a-day SessionStart reminder (`mempalace-sync-reminder.ps1`)
  covers an uninstalled checkout and a sync older than a week.
- `MEMPALACE_CONVO_SKIP_HALLWAYS`: a conversation mine skips its end-of-run hallway recount, so the
  file-by-file backfill stops paying for a whole-wing recount per file; `mempalace hallways --rebuild`
  runs once after the re-chunk. Two tests in `test_convo_miner_unit.py`.

### Stumbled on
- Importing `miner` costs 1.1 s, against the hooks' 500 ms budget — hence the helper moved out instead
  of being imported from `miner`.
- Most historical sessions ran in worktrees that have since been deleted, so root detection cannot help
  them; the routes carry the history, detection carries live sessions.
- Without routes, legacy `D:\Novita\BlueTrader` would slug to `bluetrader`, which MemPalace's alias
  matching treats as the same wing as the existing `BlueTrader` (the new app).
- Upstream ignores `.claude/`, so this diary needs `git add -f` on every commit, even though it is
  tracked.
- The backfill ran at about half the expected rate: small BlueTrader files took 48 s against 19 s for
  the same size in a small wing. Each mine recounts every name pair across its whole wing (~90k
  drawers for BlueTrader) and the next file's recount replaces the result — about 29 s per file,
  inferred from the timings and the hallway code, not profiled.

### Decided
- Root detection reads `.git` markers instead of running `git rev-parse` as #2939 proposes: no
  subprocess in the hook, and `gitdir.py` already did the reading. (Claude)
- Routes are matched on the resolved root, falling back to the raw cwd when the folder is gone. (Claude)
- Wing names keep the existing scheme through routes (`BlueTrader-New*` → `BlueTrader`,
  `BlueTrader` → `BlueTrader-Old`, `~` → `claude-config`). (User)
- A real GitHub fork, no upstream PR or comment. (User) A plain private repo came first, because GitHub
  cannot make a fork of a public repo private; the user deleted it in favour of a proper, public fork.
- Track upstream `develop` rather than the release tags, as a single commit on top. (User) The fork
  therefore runs MemPalace's unreleased code between releases.
- Defer hallways during the backfill and rebuild them once at the end, rather than per file. (User)
  Rejected: mining whole folders in one process, which pays the recount once but also files the
  3,500 non-transcript files in the backup tree.

### Open
- Install the fork into the `uv` tool only after the backfill and re-chunk runs finish, then add
  `wing_routes` to `~/.mempalace/config.json` and wire the session-end hook.
- Point the backfill script at the same wing logic and skip backup copies of live-mined sessions.
- First real `-SyncUpstream` with upstream commits to rebase over: so far the script has only run with
  nothing to rebase.
