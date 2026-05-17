# Glossary

Use this as a fast lookup while supervising coding-agent work.

## Terminal and shell

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| Terminal | Text-based place where commands are entered and output appears. | Agents run tests, builds, launches, and Git commands there. | What did this command do, and did it change anything? |
| Shell | Program that interprets terminal commands. | Bash, zsh, and PowerShell differ. | Which shell was this written for? |
| Bash | Common Unix-style shell. | Many agent commands use Bash syntax. | Will this work on my machine? |
| zsh | Common macOS shell. | Mac terminals often use zsh. | Is this zsh-compatible? |
| PowerShell | Windows shell with different syntax. | Windows instructions may use PowerShell. | Is there a PowerShell version? |
| Command | Instruction executed by the shell. | Agents run commands constantly. | Is it read-only, changing files, testing, building, launching, or live-sensitive? |
| Program | First executable token, such as git, npm, uv, python, curl. | Identifies the tool being invoked. | What program is being run? |
| Subcommand | Secondary action, such as status in git status. | Many tools use subcommands. | What action is requested? |
| Flag | Option beginning with - or --. | Flags alter command behavior. | What does this flag change? |
| Argument | Value passed to a command. | Arguments identify targets. | What file, URL, symbol, or value is targeted? |
| Working directory | Folder where the command runs. | Wrong folders cause misleading errors. | Where was this run from? |
| stdout | Normal command output. | Agents paste it as evidence. | Is this normal output? |
| stderr | Error or diagnostic output. | Some tools print warnings there. | Did the exit code still pass? |
| Exit code | Numeric command result. Zero usually means success. | Agents may use it to claim success. | What was the exit code? |
| Pipe | Sends one command output into another. | Agents filter logs/search results. | What output is passed forward? |
| Redirect | Sends output to a file or discards it. | Agents may hide or save output. | Where did the output go? |

## Files and paths

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| File | Named unit of content. | Agents inspect and edit files. | What kind of file is this? |
| Folder / directory | Container for files. | Repo structure is folder-based. | What does this folder imply? |
| Path | Location of a file or folder. | Every change and many commands include paths. | Is this source, tests, docs, config, script, or local state? |
| Absolute path | Full path from machine root. | Removes ambiguity. | Does it point to the intended repo? |
| Relative path | Path from current working directory. | Most repo commands use relative paths. | Relative to what folder? |
| Repo root | Top-level Git project folder. | Many commands must run there. | What command confirms the repo root? |
| Extension | Filename suffix like .py, .md, .toml. | Suggests file type. | What does the extension imply? |
| Hidden file | File beginning with dot. | Hidden files can be critical. | Is it safe to inspect or commit? |
| .env | Environment-variable file that may contain secrets. | Agents may reference it for config. | Did it contain real secrets? |
| .state | Local runtime state/cache/token folder. | Apps may store generated state there. | Is it excluded from Git? |

## Git

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| Git | Version-control tool. | Tracks what changed. | What does Git say changed? |
| GitHub | Hosted Git platform. | Remote repo may live there. | Is work local or pushed? |
| Repository | Project tracked by Git. | Agents work inside repos. | Which repo is active? |
| Branch | Named line of development. | Work may be on main or feature branch. | What branch is checked out? |
| main | Common primary branch. | Some work happens directly there. | Is direct work on main expected? |
| Working tree | Current repo files and changes. | Git status reports it. | Is it clean or dirty? |
| Staged change | Change prepared for commit. | Agents stage before commit. | Will this be included? |
| Unstaged change | Changed file not staged. | May be omitted from commit. | Should it be staged? |
| Untracked file | New file Git is not tracking. | New tests/docs/scripts start untracked. | Should it be added or ignored? |
| Commit | Saved checkpoint. | Agents may commit finished work. | What files are in the commit? |
| Commit hash | Unique commit identifier. | Used as a checkpoint reference. | Which exact commit? |
| Diff | Line-by-line change evidence. | Proves what actually changed. | Does the diff support the claim? |
| Remote | Linked GitHub repo. | Local work may not be remote. | Was it pushed? |
| Push | Send local commits to remote. | Makes work visible on GitHub. | Was the commit pushed? |
| Pull | Bring remote changes local. | Updates repo before work. | Could this conflict? |

## Repo structure

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| src | Source-code folder. | Often affects runtime behavior. | Is this on the app path? |
| tests | Automated tests folder. | Agents add/update tests. | Do these cover the change? |
| docs | Documentation folder. | Explains behavior. | Was docs-only work overclaimed? |
| scripts | Utility/launch/check scripts. | Agents add commands here. | Was the script actually run? |
| config | Settings files/folders. | Can affect broad behavior. | What behavior does this config affect? |
| package.json | JavaScript/TypeScript project file. | npm scripts/dependencies live here. | Which script changed? |
| pyproject.toml | Python project config. | Dependencies/tooling may live here. | Did this affect dependency/test/lint behavior? |
| README.md | Main project overview. | Agents update setup docs. | Is this only documentation? |
| .gitignore | Tells Git what to ignore. | Protects local/generated files. | Were secrets already tracked? |

## Tests

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| Test | Check for expected behavior. | Agents use tests as evidence. | What behavior is tested? |
| Unit test | Small isolated logic test. | Fast focused verification. | What unit is isolated? |
| Integration test | Multiple parts together. | Verifies wiring between components. | Which components? |
| Regression test | Prevents old bug returning. | Agents add one after fixes. | What bug does it guard? |
| Smoke test | Shallow startup/workflow check. | Proves basic viability. | What did it actually smoke? |
| Live smoke | Narrow live-service check. | Needed for live-data proof. | Was explicit live opt-in used? |
| Dry run | Safe run without live effects. | Tests readiness without risk. | What did dry-run skip? |
| Fixture | Controlled test data. | Deterministic tests use it. | Was fixture proof called live? |
| Mock | Fake replacement service. | Avoids real external calls. | What service was replaced? |
| Assertion | Expected truth inside a test. | Failures show bad assertions. | What did it expect? |
| Skipped test | Test that did not run. | Important paths may be skipped. | Which tests were skipped and why? |
| Full suite | Broad collected test set. | Regression confidence. | Does it include this feature? |
| Targeted test | Specific focused test. | Fast proof for one path. | Why is this the right target? |

## App runtime

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| Runtime | App while executing. | Code must affect runtime to matter. | Did this run in the actual app? |
| Launch | Starting app/process. | Agents start apps/scripts. | Was the app actually launched? |
| Localhost | Current machine as server. | Local apps use localhost URLs. | Does this prove only local behavior? |
| Server | Process responding to requests. | Apps often start servers. | Which port? |
| Port | Numbered server endpoint. | Local apps use ports like 5173/8000. | Was expected port responding? |
| Environment variable | Named runtime setting. | Config/modes/secrets may use it. | Is it safe to print? |
| Dependency | Required package/tool. | Missing dependencies break startup. | Is this code or environment? |
| Log | Runtime output. | Agents diagnose from logs. | What exact line proves the issue? |
| Stack trace | Error path. | Shows where code failed. | What is first relevant project file? |
| State | Stored app/session/cache data. | Affects UI/runtime behavior. | Is this app, fixture, or local state? |
| UI surface | Visible app area. | Operator-facing changes appear there. | Where can the operator see it? |
| Workflow path | User action sequence. | Tests may miss real path. | Was actual workflow exercised? |

## Coding agents

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| Coding agent | Tool that inspects, edits, runs commands, summarizes. | Main tool being supervised. | What actions did it take? |
| Tool call | Agent action through a tool. | Transcripts may show them. | Was this read, write, command, or external? |
| Repo inspection | Reading files before editing. | Agents inspect to understand context. | Did inspection lead to implementation? |
| Patch | Structured set of edits. | Agents apply patches. | What files did the patch change? |
| Summary | Agent explanation. | Can overclaim. | Which parts are facts? |
| Overclaim | Claim beyond evidence. | Common with live/test claims. | What evidence is missing? |
| Hallucinated confidence | Confident tone without proof. | Summaries may sound certain. | What backs the confidence? |
| Prompt stack | Sequenced prompts for large task. | Complex course/app work may need stages. | Which stage is this? |
| Handoff | Transfer summary. | Carries context forward. | Does it include files, tests, blockers, next step? |

## Live data and safety

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| Live data | Real external data at runtime. | Some apps depend on APIs/markets. | Was data actually live? |
| Production | Real operational environment. | Higher risk than local tests. | Could this affect users/data/money? |
| Credential | Access value. | Live tests may need it. | Was it protected? |
| Secret | API key/token/password/client secret. | May live in .env. | Was it printed or committed? |
| Token | Credential for authenticated access. | OAuth/API flows use it. | Where is it stored? |
| API key | Secret string for API access. | May be passed via env var. | Was it redacted? |
| Read-only | Observation-only mode. | Safer live checks use it. | Can it mutate anything? |
| Manual opt-in | Explicit user approval for live/risky action. | Live should not happen by default. | Where is the opt-in? |
| Fallback | Backup path after primary failure. | Can hide live failure. | Could fixture data mask failure? |
| Fail closed | Block when uncertain. | Safer default. | Did it block or continue? |
| Sanitized output | Sensitive values removed. | Prevents leaks. | Does output expose secrets? |
| Guardrail | Rule preventing unsafe behavior. | Repos encode safety. | Which guardrail applies? |

## Orchestration prompts

| Term | Plain-English definition | Why the learner sees it | What to ask when confused |
|---|---|---|---|
| Task scope | Boundary of work. | Prevents broad drift. | Did the agent stay in scope? |
| Constraint | Rule agent must obey. | Protects correctness/safety. | Was any constraint violated? |
| Acceptance criteria | Required completion conditions. | Makes success measurable. | Which passed or failed? |
| Source of truth | Authoritative spec/file/instruction. | Prevents invention. | What source was used? |
| Implementation-first | Focus on working behavior. | Counters audit-only loops. | What app behavior changed? |
| Audit-only | Inspection without implementation. | Useful for diagnosis only. | Was this requested? |
| Diagnosis | Finding cause. | Needed before some fixes. | What concrete fix follows? |
| Verification command | Command checking success. | Turns claims into evidence. | What did it prove? |
| Stop condition | Rule to stop instead of guess. | Prevents unsafe continuation. | Did the agent stop correctly? |
| Follow-up prompt | Next focused instruction. | Reduces uncertainty. | What is the narrow next question? |
| Regression risk | Chance of breaking old behavior. | Larger diffs increase risk. | What could this break? |
| Operator-facing behavior | Behavior visible to app user. | Goal of real implementation. | What can the operator now do? |
