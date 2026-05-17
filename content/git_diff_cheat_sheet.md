# Git & Diff Cheat Sheet

A condensed reading guide for the Git output you will see most often.

## `git status --short` codes

The first column is the staging area, the second column is the working tree.

| Code | Meaning |
|---|---|
| ` M` | Modified, unstaged. Not included in the next commit yet. |
| `M ` | Modified, staged. Will be in the next commit. |
| `MM` | Modified, partially staged and partially unstaged. The next commit will not include the unstaged portion. |
| `A ` | Added (new file), staged. |
| `D ` | Deleted, staged. |
| `R ` | Renamed, staged. |
| `??` | Untracked. New file Git is not following yet. |

## Reading a diff block

```diff
diff --git a/src/cockpit/renderer.py b/src/cockpit/renderer.py
@@ -42,7 +42,12 @@ def render_manual_query(state):
     if state.is_blocked:
-        return ""
+        reason = state.blocked_reason or "unknown reason"
+        return f"Blocked: {reason}"
     return state.result_summary
```

Read it like this:

- **`diff --git a/... b/...`** — which file changed.
- **`@@ -42,7 +42,12 @@`** — line range in the old file, then the new file.
- **Function or context line** (after `@@`) — the surrounding code, for orientation.
- **Lines starting with `-`** — removed.
- **Lines starting with `+`** — added.

For every changed file, ask:

- Is this **source, test, docs, config, script, or generated state**?
- Is the changed function actually on the runtime path the user touches?
- Are there tests that exercise this change?

## Branch and commit checks

| Command | What it answers |
|---|---|
| `git branch --show-current` | Which branch am I on? |
| `git status --short` | What is modified, staged, or untracked? |
| `git diff` | What are the unstaged changes? |
| `git diff --staged` | What is in the next commit? |
| `git diff --stat` | Which files changed and by how many lines? |
| `git log --oneline -5` | What were the last 5 commit messages? |
| `git show <hash>` | What did a specific commit change? |
| `git log @{u}..HEAD --oneline` | Which commits are local-only (not pushed)? |

## What a clean tree does NOT prove

- The app runs.
- The tests pass.
- The work was pushed.
- The diff was reviewed.
- The feature works for a real user.

A clean tree only proves: nothing is uncommitted right now.

## When you see "ahead by N commits"

```text
Your branch is ahead of 'origin/<branch>' by 2 commits.
```

This means the work is committed locally but not yet pushed. Ask:

- Should this be pushed?
- Is anyone else going to look at it?
- Was the verification run before commit or after?
