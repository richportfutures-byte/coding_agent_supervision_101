# Course Guide

## Course premise

Coding Agent Supervision 101 teaches non-developers how to supervise coding agents building or modifying real software projects. The goal is not to become a full-time developer. The goal is to understand what agents execute, what they change, what they verify, what they skip, and what claims should be challenged.

The core supervision distinction is **activity versus progress**. An agent can inspect files, run commands, and write a long report without improving the app. A useful supervisor asks for changed files, exact commands, verification scope, data source, and what now works.

## Who this is for

This course is for people who use tools like Codex, Claude Code, Gemini CLI, Windsurf, or similar coding agents to work in GitHub repositories, but who do not yet read terminal output, Git state, diffs, tests, or runtime claims comfortably.

## How to use this notebook

Use the section selector to move between lessons, glossary, workbook drills, command examples, and the agent-output triage form. Keep the notebook open during real agent sessions. After an agent finishes, use the triage checklist before trusting the result.

## Verification mindset

Separate every agent claim into:

1. **Fact**: what is directly visible in files, commands, output, or Git state.
2. **Interpretation**: what those facts probably mean.
3. **What to verify**: what remains unproven.
4. **Next prompt**: the narrow question that reduces uncertainty.

## Module 1: What a coding agent is actually doing

A coding agent may inspect files, edit files, run commands, run tests, read errors, create commits, report results, get blocked, or overclaim confidence. Your job is to determine whether it changed the right thing and verified the right thing.

### Example

```text
I inspected the launch script, updated the cockpit renderer, and 6 tests passed.
```

**Fact:** The agent claims inspection, a renderer change, and tests.

**Interpretation:** This may be implementation if the renderer is on the active app path.

**What to verify:** Which files changed? Which tests ran? Did the app launch? Was the data live, mock, fixture, or unknown?

### Beginner misunderstanding

“The agent said it fixed it, so it is fixed.” Not enough. The summary is a claim. Evidence is changed files, relevant tests, runtime proof, and explicit limits.

## Module 2: Terminal and shell basics

A terminal is where commands run. A shell interprets commands. Bash, zsh, and PowerShell differ. A command usually looks like:

```bash
program subcommand --flag value path/to/file
```

Example:

```bash
uv run pytest -q tests/test_runtime_gate.py
```

Read it as: `uv` runs `pytest`; `-q` is quiet mode; `tests/test_runtime_gate.py` is the target test file.

### What to ask

```text
Classify the command: read-only, file-changing, install/build, test, app launch, or live-data-sensitive.
```

## Module 3: Files, paths, and repo structure

A file path tells you what kind of work happened.

- `src/` usually means source code.
- `tests/` usually means automated tests.
- `docs/` usually means documentation.
- `scripts/` may contain launch, utility, or verification scripts.
- `.env` may contain secrets.
- `.state` may contain local runtime state or tokens.

### Example

```text
Files changed:
- src/runtime/live_adapter.py
- tests/test_live_adapter.py
- docs/live_data.md
```

This has the shape of real implementation because source, tests, and docs changed. Still verify whether the source file is on the runtime path.

## Module 4: Git fundamentals

Git is the audit trail. It tells you what changed, whether work is committed, whether the tree is clean, and whether a commit exists.

Useful commands:

```bash
git status --short
git diff --stat
git diff
git log --oneline -5
git branch --show-current
```

A clean tree proves no uncommitted changes. It does **not** prove the app works.

## Module 5: Tests and verification

Passing tests prove only that the selected tests passed under the tested conditions.

A focused test:

```bash
uv run pytest -q tests/test_runtime_gate.py
```

```text
7 passed in 0.82s
```

This proves the collected tests in that file passed. It does not prove full app launch, browser behavior, live data, or untested workflows.

## Module 6: Runtime and launch concepts

Code existing in a repo is not the same as a running app. Runtime means the app is actually executing.

A launch output like:

```text
Local: http://localhost:5173/
```

proves the app shell started enough to provide a URL. It does not prove the target feature works.

## Module 7: Reading coding-agent prompts

Good prompts specify goal, scope, constraints, acceptance criteria, safety boundaries, and verification commands.

Weak prompt:

```text
Fix the app and make it better.
```

Stronger prompt:

```text
Implement blocked-query reason display. Modify only src/cockpit and tests unless narrow config is required. Do not touch live broker execution code. Add focused tests and report what operator-visible behavior now works.
```

## Module 8: Reading coding-agent output

A final agent response is an evidence package. It should include:

- files changed
- commands run
- test results
- what now works
- what was not verified
- blockers
- Git state
- data source: live, fixture, mock, dry-run, static, or unknown

A vague summary like “Done, all tests pass” is not enough.

## Module 9: Live data and safety

Live-data work requires explicit manual opt-in, redacted output, read-only scope when possible, no secret printing, and no fixture fallback after live failure.

Good live proof has this shape:

```text
opt_in_live=yes
mode=live
provider=schwab
quotes_received=1
fallback_on_failure=no
secrets_in_output=no
```

Dry-run proof and fixture proof are useful, but they are not live proof.

## Module 10: Supervising the build loop

After every agent run, ask:

```text
What changed? Which files changed? What commands ran? What did those commands prove? What was not verified? What remains blocked? What is the next concrete implementation step?
```
