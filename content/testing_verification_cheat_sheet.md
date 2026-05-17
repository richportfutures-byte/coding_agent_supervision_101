# Testing & Verification Cheat Sheet

A pocket reference for what a test result actually proves — and where it stops.

## Verification ladder

Each rung proves more than the one below it. A run is only as strong as the highest rung it actually reached.

| Level | Example | Proves | Does not prove |
|---|---|---|---|
| Single unit test | `pytest tests/test_x.py::test_y` | One function under one condition. | Other functions, integration, runtime, live. |
| Focused test file | `uv run pytest -q tests/test_x.py` | The collected tests in that one file. | Other files, app launch, browser, live. |
| Full test suite | `uv run pytest -q` | The collected suite passed under the configured conditions. | UI, operator workflow, live data, anything skipped or deselected. |
| Build success | `npm run build` | The bundle compiles. | Tests passed, UI works, runtime behavior is correct. |
| Smoke (fixture/mock) | App boots with fake data. | Wiring against fakes works. | Real provider behavior or live data. |
| Smoke (dry run) | `--dry-run` flag | The code path is reachable without live effects. | The non-dry-run path was exercised. |
| Smoke (live, bounded) | One read-only live API call with explicit opt-in. | A narrow live path works under bounded conditions. | Broader live coverage, write paths, multi-symbol/multi-user behavior. |
| Operator workflow exercised | Real user action in the running app. | The feature works end-to-end as a person would use it. | All edge cases, performance, multi-tenant correctness. |

## Words that look like verification but are not

- "Done." — no command, no output.
- "All tests pass." — no command, no pass/fail/skip counts.
- "Build succeeded." — build is not test.
- "Working tree is clean." — no behavior is proven.
- "App is running at http://localhost:..." — only proves a process bound a port.
- "Coverage is at 92%." — coverage is a footprint, not a result.

## Five questions to ask after any verification claim

1. What was the exact command?
2. What was the exact output, including pass/fail/skip counts?
3. Which part of the system was exercised?
4. What was the data source — live, mock, fixture, dry-run, static, or unknown?
5. What was NOT tested or NOT exercised by this run?

## When a test fails

- Read the test name. Does it encode the desired behavior?
- If yes, fix the code, not the test.
- If no, fix the test and explain why.
- Never delete or skip a failing test just to make CI green.

## When tests are skipped

A skipped test is not a passing test. Always ask:

- Which exact tests were skipped?
- Why were they skipped — missing credentials, platform, environment, marker?
- What would it take to run them?
