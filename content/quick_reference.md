# After a Coding Agent Finishes, Read This First

Use this after every coding-agent run.

## First classify the result

| Classification | What it means | What to ask next |
|---|---|---|
| Implemented and verified | Source/config/script behavior changed and relevant verification ran. | What exactly now works, and what was not verified? |
| Implemented but not verified | Source/config/script changed, but tests/runtime proof are missing or thin. | What focused test or smoke should be run now? |
| Implemented but not runtime-verified | Tests passed, but app launch/browser/operator workflow was not exercised. | What launch or runtime smoke proves the operator path? |
| Test-only | Tests changed or ran, but no source/runtime implementation is visible. | What source change makes the test pass? |
| Docs-only | Markdown/docs changed only. | Do not call this implemented. Which runtime file enforces it? |
| Audit-only | Agent inspected and recommended but did not change behavior. | Implement the smallest concrete change unless blocked. |
| Blocked | Agent could not proceed due to missing credentials, environment, permissions, unclear scope, or safety boundary. | What completed before the blocker, and what removes the blocker? |
| Unsafe or unclear | Secrets, destructive commands, live action, production mutation, or unsupported fallback may be involved. | Stop and require a fact/interpretation/unverified-claim breakdown. |
| Needs follow-up | Summary lacks changed files, commands, test output, or Git state. | Ask for complete evidence package. |

## Minimum evidence package

A good final agent summary includes:

- Goal attempted
- Files changed
- File classification: source, test, docs, config, script, generated/local state
- Commands run
- Tests passed, failed, skipped, or not run
- Whether the app launched
- Whether the operator workflow was exercised
- Data source: live, mock, fixture, dry-run, static, or unknown
- What now works
- What was not verified
- Blockers
- Git branch, commit hash if committed, pushed/local status

## Red flags

- “Done” with no files or commands
- “All tests pass” with no command or counts
- “Live verified” when output says mock, fixture, dry_run, or no live opt-in
- Docs-only changes claimed as implementation
- Test-only changes claimed as implementation
- Clean Git tree claimed as proof the app works
- Build success claimed as proof the workflow works
- App launch URL claimed as proof the feature works
- Silent fallback from failed live data to fixture data
- Real secrets printed in output

## Good follow-up prompts

```text
List changed files, exact commands, test results, what now works, what was not verified, blockers, and Git state.
```

```text
Classify every changed file as source, test, docs, config, script, generated state, or unknown. Identify the changed file that actually affects runtime behavior.
```

```text
Label each verification command as mock, fixture, dry-run, or live. If live, show explicit opt-in, redacted output, data source, timestamp if available, and whether fixture fallback was impossible.
```

```text
This is audit-only. Implement the smallest concrete behavior change now unless blocked. If blocked, name the exact blocker and next implementation step.
```

## Core rule

Do not trust confidence. Trust evidence.
