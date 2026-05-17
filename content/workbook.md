# Workbook

This workbook trains a non-developer to read coding-agent work without needing to write production code. For each drill, ask:

1. What is directly visible?
2. What is a reasonable interpretation?
3. What cannot be safely concluded?
4. What should I ask the coding agent next?

# Section 1: Command Dissection Drills

Each drill asks: what program is being run, what target is used, what flags are used, what is the command trying to prove, what success looks like, and what failure looks like.

## Drill 1.1 - Git status check

```bash
git status --short
```

## Drill 1.2 - Focused Python test file

```bash
uv run pytest -q tests/test_runtime_gate.py
```

## Drill 1.3 - Frontend build

```bash
npm run build -- --mode production
```

## Drill 1.4 - Local health endpoint check

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/health
```

## Drill 1.5 - App launch with an environment variable

```bash
API_BASE_URL=http://localhost:8000 uv run python scripts/launch_app.py --dry-run
```

## Drill 1.6 - Frontend dev server with host and port

```bash
NODE_ENV=development npm run dev -- --host 127.0.0.1 --port 5173
```

## Drill 1.7 - Bounded live smoke script

```bash
SCHWAB_API_KEY=*** uv run python scripts/run_live_smoke.py --opt-in-live --symbol SPY --max-calls 1 --read-only
```

## Drill 1.8 - Search for fallback behavior

```bash
grep -R "fallback_to_fixture" -n src tests
```

## Drill 1.9 - Inspect a specific file diff

```bash
git diff -- src/cockpit/manual_query.py
```

## Drill 1.10 - Fixture operator session script

```bash
uv run python scripts/run_fixture_operator_session.py --contracts ES,NQ,CL,6E,MGC --no-live
```

# Section 2: Git Output Drills

## Drill 2.1 - Short status with modified and untracked files

```text
 M src/runtime/session.py
?? tests/test_session_runtime.py
```

## Drill 2.2 - Staged and unstaged version of the same file

```text
MM src/cockpit/renderer.py
M  tests/test_cockpit_renderer.py
```

## Drill 2.3 - Clean tree

```text
On branch feature/runtime-readiness
nothing to commit, working tree clean
```

## Drill 2.4 - Branch name

```bash
git branch --show-current
```

```text
main
```

## Drill 2.5 - Recent commits

```text
9f86daa Add cockpit blocked-reason display
17f62bd Wire runtime readiness gate
4b219af Add fixture cockpit launch command
```

## Drill 2.6 - Diff stat with mixed file types

```text
 docs/operator_guide.md          |  8 ++++++--
 src/cockpit/manual_query.py     | 22 ++++++++++++++++++----
 tests/test_manual_query.py      | 14 ++++++++++++++
 3 files changed, 40 insertions(+), 4 deletions(-)
```

## Drill 2.7 - Commit created

```text
[feature/cockpit-blocked-reason 5ca10fd] Show blocked manual-query reason in cockpit
 3 files changed, 42 insertions(+), 8 deletions(-)
```

## Drill 2.8 - Local commit not pushed

```text
Your branch is ahead of 'origin/feature/cockpit-blocked-reason' by 1 commit.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

# Section 3: Diff-Reading Drills

## Drill 3.1 - Blocked reason display

```diff
diff --git a/src/cockpit/renderer.py b/src/cockpit/renderer.py
@@ -42,7 +42,12 @@ def render_manual_query(state):
     if state.is_blocked:
-        return ""
+        reason = state.blocked_reason or "unknown reason"
+        return f"Blocked: {reason}"
     return state.result_summary
```

## Drill 3.2 - Test-only addition

```diff
diff --git a/tests/test_manual_query.py b/tests/test_manual_query.py
@@ -0,0 +1,8 @@
+def test_blocked_query_has_reason():
+    state = make_blocked_state(reason="missing credentials")
+    result = render_manual_query(state)
+    assert "missing credentials" in result
```

## Drill 3.3 - Documentation-only update

```diff
diff --git a/docs/live_data.md b/docs/live_data.md
@@ -12,3 +12,9 @@ Live data setup
+Live mode must be started manually.
+Fixture data must never be described as live data.
+If live connection fails, the app should block instead of silently falling back.
```

## Drill 3.4 - Config change in package script

```diff
diff --git a/package.json b/package.json
@@ -7,6 +7,7 @@
   "scripts": {
     "dev": "vite",
+    "smoke": "node scripts/smoke-check.mjs",
     "build": "vite build"
   }
```

## Drill 3.5 - Launch script adds dry-run flag handling

```diff
diff --git a/scripts/launch_operator_cockpit.py b/scripts/launch_operator_cockpit.py
@@ -18,6 +18,10 @@ def main(argv):
     parser.add_argument("--port", default="2718")
+    parser.add_argument("--dry-run", action="store_true")
     args = parser.parse_args(argv)
+
+    if args.dry_run:
+        print("launch_mode=dry_run live_connection=no")
+        return 0
```

# Section 4: Test-Output Drills

## Drill 4.1 - Focused passing tests

```bash
uv run pytest -q tests/test_runtime_gate.py
```

```text
.......                                                                  [100%]
7 passed in 0.82s
```

## Drill 4.2 - Failing test

```text
....F..                                                                  [100%]
FAILED tests/test_runtime_gate.py::test_runtime_blocks_without_credentials
1 failed, 6 passed in 0.91s
```

## Drill 4.3 - Skipped tests

```text
.......s.s..s...                                                         [100%]
13 passed, 3 skipped in 1.24s
```

## Drill 4.4 - Full suite pass

```text
200 passed in 12.42s
```

## Drill 4.5 - Build passes but tests are not run

```bash
npm run build
```

```text
✓ 312 modules transformed.
✓ built in 1.17s
```

## Drill 4.6 - Mocked fixture test

```text
5 passed in 0.22s
```

Test names include fixture rendering, source labels, no live credentials, missing timestamp blocking, and limited contract scope.

## Drill 4.7 - Dry-run smoke

```text
mode=dry_run
provider=mock
live_connection=no
result=ready_to_run_with_manual_live_opt_in
```

## Drill 4.8 - Bounded live smoke

```text
opt_in_live=yes
mode=live
provider=schwab
quotes_received=1
fallback_on_failure=no
secrets_in_output=no
result=live_quote_received
```

# Section 5: Agent-Summary Triage Drills

## Drill 5.1 - Strong implementation summary

```text
Implemented blocked-query reason display.
Files changed: src/cockpit/manual_query.py, src/ui/cockpit_renderer.py, tests/test_manual_query.py
Verification: uv run pytest -q tests/test_manual_query.py, 8 passed
Not verified: browser launch, live-data mode
```

## Drill 5.2 - Weak generic summary

```text
Done. I fixed the issue and all tests pass.
```

## Drill 5.3 - Documentation-only work overclaimed as implementation

```text
Implemented live data safety.
Files changed: docs/live_data_safety.md, docs/operator_setup.md
Verification: spellcheck passed
```

## Drill 5.4 - Test-only work

```text
Added coverage for missing credentials behavior.
Files changed: tests/test_runtime_gate.py
Verification: 1 failed, 6 passed
```

## Drill 5.5 - Audit-only result when implementation was requested

```text
Inspected the launch path and recommended changing the renderer. No files were modified.
```

## Drill 5.6 - Partially blocked by missing credentials

```text
Files changed: src/runtime/provider_factory.py, tests/test_provider_factory.py
Verification: 5 passed
Blocked: Could not run live smoke because credentials are not configured.
```

## Drill 5.7 - Mocked proof overstated as live proof

```text
Live market data is verified.
Tests used fixture quotes. Did not run live mode.
```

## Drill 5.8 - Good live smoke report

```text
Ran a bounded live smoke. mode=live provider=schwab quotes_received=1 fallback_on_failure=no secrets_in_output=no
```

## Drill 5.9 - Busywork refactor summary

```text
Renamed local variables and reordered imports. No tests run.
```

## Drill 5.10 - Commit-focused but verification-light summary

```text
Committed the fix. Commit: 5ca10fd. Final git status: clean.
```
