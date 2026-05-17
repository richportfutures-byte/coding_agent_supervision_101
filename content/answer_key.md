# Answer Key

Use this answer key to compare your read against the intended supervisor interpretation.

## Answer Key for Section 1: Command Dissection Drills

### Answer 1.1 - Git status check

Program: `git`. Target: current repository working tree. Flag: `--short`. It proves changed/staged/unstaged/untracked file state. It does not prove the app works. Ask whether changes were pre-existing and whether new files should be committed.

### Answer 1.2 - Focused Python test file

Program: `uv`, running `pytest`. Target: `tests/test_runtime_gate.py`. Flag: `-q`. It proves only the selected test file passed or failed. It does not prove app launch, UI, or live data.

### Answer 1.3 - Frontend build

Program: `npm`, running the `build` script. `--mode production` is passed to the build tool. It proves the frontend compiles in production mode. It does not prove the operator workflow works in the browser.

### Answer 1.4 - Local health endpoint check

Program: `curl`. Target: local health endpoint. Flags make curl silent, discard body, and print HTTP status code. It proves a local endpoint responds. It does not prove the full app works.

### Answer 1.5 - App launch with an environment variable

Environment variable: `API_BASE_URL=http://localhost:8000`. Program: `uv` running Python. Target: `scripts/launch_app.py`. Flag: `--dry-run`. It proves the dry-run path, not actual launch or live service.

### Answer 1.6 - Frontend dev server with host and port

Program: `npm` running `dev`. Env var: `NODE_ENV=development`. Flags: host and port. It proves the dev server can start if successful. It does not prove the target screen was tested.

### Answer 1.7 - Bounded live smoke script

Program: `uv` running Python. Env var is redacted. Target: `scripts/run_live_smoke.py`. Flags request explicit live opt-in, one symbol, max one call, read-only. It can prove a narrow live read if output confirms live mode, quote received, no fallback, and no secrets.

### Answer 1.8 - Search for fallback behavior

Program: `grep`. Flags: recursive search with line numbers. Target: `src` and `tests`. It locates references to `fallback_to_fixture`. It does not prove fallback is safe without reading matched code.

### Answer 1.9 - Inspect a specific file diff

Program: `git diff`. Target: `src/cockpit/manual_query.py`. It shows unstaged changes for that file. It does not show staged changes unless `--staged` is used.

### Answer 1.10 - Fixture operator session script

Program: `uv` running Python. Target: fixture session script. Flags select contracts and no-live mode. It proves fixture/no-live behavior only. It does not prove live market data.

## Answer Key for Section 2: Git Output Drills

### Answer 2.1 - Short status with modified and untracked files

`src/runtime/session.py` is modified and tracked. `tests/test_session_runtime.py` is new and untracked. Work is not committed. You cannot know whether changes were pre-existing. Ask whether the new test should be added.

### Answer 2.2 - Staged and unstaged version of the same file

`MM src/cockpit/renderer.py` means the file has both staged and unstaged changes. The next commit would not include all current renderer changes unless the unstaged part is staged. Ask for staged and unstaged diffs separately.

### Answer 2.3 - Clean tree

The branch is `feature/runtime-readiness`, and there are no uncommitted changes. This does not prove the app works and does not prove the branch was pushed.

### Answer 2.4 - Branch name

The current branch is `main`. Ask whether direct-to-main work is expected or whether a feature branch should be used.

### Answer 2.5 - Recent commits

The latest shown commit is `9f86daa`. Commit messages suggest topics but do not prove file changes or tests. Ask for `git show --stat` and verification commands.

### Answer 2.6 - Diff stat with mixed file types

Docs, source, and tests changed. This has the shape of real implementation, but correctness requires reading the actual diff and test output.

### Answer 2.7 - Commit created

A commit was created on branch `feature/cockpit-blocked-reason` with hash `5ca10fd`. It does not prove tests passed or that the commit was pushed.

### Answer 2.8 - Local commit not pushed

The branch is one commit ahead of remote and the tree is clean. Work is committed locally but not published. Ask whether to push or keep local for review.

## Answer Key for Section 3: Diff-Reading Drills

### Answer 3.1 - Blocked reason display

Source/UI rendering changed. It likely changes operator-visible behavior because blocked states now return a visible string. Verify that `render_manual_query` is on the active UI path and has focused tests.

### Answer 3.2 - Test-only addition

A test file changed. Tests do not directly implement runtime behavior. Ask what source change makes the test pass and whether the test failed before implementation.

### Answer 3.3 - Documentation-only update

Docs changed only. No direct app behavior changed. Ask which runtime file enforces the safety rule.

### Answer 3.4 - Config change in package script

`package.json` changed and adds an npm script. It may add a useful command, but it is not direct app behavior. Run `npm run smoke` and inspect what it actually checks.

### Answer 3.5 - Launch script adds dry-run flag handling

A script changed. It adds a dry-run path. Verify both `--dry-run` and normal launch behavior.

## Answer Key for Section 4: Test-Output Drills

### Answer 4.1 - Focused passing tests

The selected test file passed. It does not prove full app launch, UI workflow, or live data.

### Answer 4.2 - Failing test

One test failed. Do not delete the test just to get green output. Ask whether the test encodes the desired behavior and then fix code or test accordingly.

### Answer 4.3 - Skipped tests

Some tests passed and some did not run. Skipped tests are not passing tests. Ask which tests were skipped and why.

### Answer 4.4 - Full suite pass

The collected suite passed. It does not prove app launch, browser workflow, live data, or untested paths.

### Answer 4.5 - Build passes but tests are not run

The frontend compiled. It does not prove tests passed or the UI workflow works.

### Answer 4.6 - Mocked fixture test

Fixture behavior passed. This is useful but not live proof.

### Answer 4.7 - Dry-run smoke

Dry-run path executed. It did not connect live. Do not call this live proof.

### Answer 4.8 - Bounded live smoke

A narrow live read is proven if the output is authentic and shows explicit opt-in, live mode, provider, quote received, no fallback, and no secrets. It does not prove all symbols, UI, or future calls.

## Answer Key for Section 5: Agent-Summary Triage Drills

### Answer 5.1 - Strong implementation summary

Likely implementation. Evidence includes source files, tests, exact test command, and explicit not-verified limits. Ask whether the renderer is on the active cockpit path.

### Answer 5.2 - Weak generic summary

Cannot classify. Missing files, commands, test output, skipped tests, Git state, and actual operator behavior.

### Answer 5.3 - Documentation-only work overclaimed as implementation

No runtime implementation is shown. Ask for the runtime file or smallest implementation step.

### Answer 5.4 - Test-only work

Tests changed and failed. This may be useful red/green setup, but implementation is missing. Ask the agent to implement the source change without weakening the test.

### Answer 5.5 - Audit-only result when implementation was requested

No implementation happened. Ask for the renderer change and focused test.

### Answer 5.6 - Partially blocked by missing credentials

Source/tests changed and focused tests passed. Live smoke is not verified. This is acceptable if secrets were protected. Ask whether provider factory is on the app launch path.

### Answer 5.7 - Mocked proof overstated as live proof

The headline overclaims. Fixture tests are not live verification. Ask the agent to restate as fixture-backed UI verification unless it can show a live smoke command.

### Answer 5.8 - Good live smoke report

This is verification, not implementation. It is strong live proof for a narrow path. Ask whether it exercises the actual app runtime path or only a standalone harness.

### Answer 5.9 - Busywork refactor summary

Probably no operator-visible implementation. Ask what behavior changed and run relevant tests before claiming safety.

### Answer 5.10 - Commit-focused but verification-light summary

Commit hash and clean tree are useful but insufficient. Ask for changed files, verification commands, pushed/local status, and what behavior changed.

## Reusable supervisor prompts

```text
List exact test commands, number of tests passed/failed/skipped/deselected, and what each command proves. Also state what these tests do not prove.
```

```text
Classify every changed file as source, test, docs, config, script, generated state, or unknown. Identify the changed file that affects runtime behavior and explain how it is on the app path.
```

```text
Label each verification command as mock, fixture, dry-run, or live. If live, show the explicit opt-in command, redacted output, data source, timestamp if available, and whether fixture fallback was impossible.
```

```text
This is audit-only. Implement the smallest concrete behavior change now unless you are blocked. If blocked, name the exact blocker and next implementation step.
```

```text
Show current branch, final git status, whether work is committed, commit hash if applicable, and whether commit is pushed or local only.
```
