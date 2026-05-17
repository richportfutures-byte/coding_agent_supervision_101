import marimo

__generated_with = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _():
    import re
    from pathlib import Path

    import marimo as mo

    ROOT = Path(__file__).parent
    CONTENT_DIR = ROOT / "content"

    def read_md(filename: str) -> str:
        _path = CONTENT_DIR / filename
        if not _path.exists():
            return f"# Missing content file\n\nExpected `{_path}`."
        return _path.read_text(encoding="utf-8")

    def split_sections(markdown_text: str, min_level: int = 1, max_level: int = 2):
        _lines = markdown_text.splitlines()
        _sections = []
        _title = "Overview"
        _current = []
        _heading_re = re.compile(rf"^(#{{{min_level},{max_level}}})\s+(.+?)\s*$")
        for _line in _lines:
            _match = _heading_re.match(_line)
            if _match and _current:
                _sections.append((_title, "\n".join(_current).strip()))
                _current = [_line]
                _title = _match.group(2).strip()
            else:
                if _match:
                    _title = _match.group(2).strip()
                _current.append(_line)
        if _current:
            _sections.append((_title, "\n".join(_current).strip()))
        return _sections

    def extract_glossary_rows(markdown_text: str):
        _rows = []
        _category = "Uncategorized"
        for _raw in markdown_text.splitlines():
            _line = _raw.strip()
            if _line.startswith("## "):
                _category = _line[3:].strip()
                continue
            if not _line.startswith("|") or "---" in _line or "Term" in _line:
                continue
            _cells = [_cell.strip().replace("**", "") for _cell in _line.strip("|").split("|")]
            if len(_cells) >= 4:
                _rows.append({
                    "category": _category,
                    "term": _cells[0],
                    "definition": _cells[1],
                    "why_seen": _cells[2],
                    "ask": _cells[3],
                })
        return _rows

    def extract_drills(markdown_text: str):
        _workbook_body = markdown_text.split("# Section 6: Answer Key", 1)[0]
        _matches = list(re.finditer(r"^## Drill\s+([^\n]+)\n", _workbook_body, re.MULTILINE))
        _drills = []
        for _index, _match in enumerate(_matches):
            _start = _match.start()
            _end = _matches[_index + 1].start() if _index + 1 < len(_matches) else len(_workbook_body)
            _id = _match.group(1).strip().split(" ", 1)[0]
            _drills.append({
                "id": _id,
                "title": f"Drill {_match.group(1).strip()}",
                "body": _workbook_body[_start:_end].strip(),
            })
        return _drills

    def extract_answers(markdown_text: str):
        _matches = list(re.finditer(r"^### Answer\s+([^\n]+)\n", markdown_text, re.MULTILINE))
        _answers = []
        for _index, _match in enumerate(_matches):
            _start = _match.start()
            _end = _matches[_index + 1].start() if _index + 1 < len(_matches) else len(markdown_text)
            _id = _match.group(1).strip().split(" ", 1)[0]
            _answers.append({
                "id": _id,
                "title": f"Answer {_match.group(1).strip()}",
                "body": markdown_text[_start:_end].strip(),
            })
        return _answers

    def extract_follow_up(answer_body: str) -> str | None:
        _matches = re.findall(r"(Ask\s+[^.!?]*[.!?])", answer_body)
        return _matches[-1].strip() if _matches else None

    def drill_category_from_id(drill_id: str) -> str:
        _first = drill_id.split(".", 1)[0]
        return {
            "1": "Command dissection",
            "2": "Git output",
            "3": "Diff reading",
            "4": "Test output",
            "5": "Agent-summary triage",
        }.get(_first, "Other")

    def classify_run(
        summary,
        files,
        commands,
        source_changed,
        tests_changed,
        app_launched,
        live,
        dry_run,
        fixture,
        docs_only,
        test_only,
        audit_only,
        blocked,
        unsafe,
    ):
        _changed = [_line.strip() for _line in files.splitlines() if _line.strip()]
        _text = "\n".join([summary, files, commands]).lower()
        _heuristic_source = any(
            _path.startswith(("src/", "app/", "scripts/")) or _path in {"package.json", "pyproject.toml"}
            for _path in _changed
        )
        _heuristic_tests = "test" in _text or any("test" in _path for _path in _changed)
        _heuristic_docs_only = bool(_changed) and all(
            _path.endswith(".md") or _path.startswith("docs/") for _path in _changed
        )
        _has_source = source_changed or _heuristic_source
        _has_tests = tests_changed or _heuristic_tests
        _has_pass = any(_token in _text for _token in ("passed", "success", "built", "ok"))

        if unsafe:
            _label = "Unsafe or unclear"
            _reason = "Safety or evidence is unclear. Do not trust the run until boundaries are explicit."
            _prompt = "Separate facts, interpretations, and unverified claims. Confirm whether secrets, live actions, destructive commands, or fallback paths were involved."
        elif blocked:
            _label = "Blocked"
            _reason = "The agent reports it could not or should not proceed. Blocked can be correct when safety or credentials prevent verification."
            _prompt = "Name the exact blocker, what was completed before the blocker, and the smallest concrete implementation step after the blocker is removed."
        elif audit_only:
            _label = "Audit-only"
            _reason = "The work appears to inspect or recommend without changing behavior."
            _prompt = "This is audit-only. Implement the smallest concrete behavior change now unless blocked."
        elif docs_only or _heuristic_docs_only:
            _label = "Docs-only"
            _reason = "Only documentation-style files are listed, so runtime behavior is not proven changed."
            _prompt = "Do not call this implemented. Identify the source/config/script file that would have to change to affect runtime behavior."
        elif test_only or (_has_tests and not _has_source):
            _label = "Test-only"
            _reason = "Tests changed or ran, but no implementation file is visible."
            _prompt = "What source change makes this test pass, and did the test fail before implementation?"
        elif _has_source and _has_tests and (app_launched or live):
            _label = "Implemented and verified"
            _reason = "Source/config/script changes are present and a real runtime path was exercised (app launch or live)."
            _prompt = "List exact changed runtime files, exact verification commands, what each command proved, and what was not verified."
        elif _has_source and _has_tests and (dry_run or _has_pass):
            _label = "Implemented but not runtime-verified"
            _reason = "Tests passed or a dry-run ran, but app launch / operator workflow was not exercised."
            _prompt = "Show a launch or runtime smoke that exercises the operator path, with the exact action and visible result."
        elif _has_source:
            _label = "Implemented but not verified"
            _reason = "Source/config/script changes are present, but verification evidence is incomplete."
            _prompt = "Run the focused tests or smallest runtime smoke for the changed operator path and report exact output."
        elif _has_tests:
            _label = "Test-only"
            _reason = "Tests changed or ran, but no implementation file is visible."
            _prompt = "What source change makes this test pass, and did the test fail before implementation?"
        else:
            _label = "Needs follow-up"
            _reason = "There is not enough structured evidence to classify the run."
            _prompt = "List changed files, exact commands, test results, what now works, what was not verified, blockers, and Git state."

        _notes = []
        if live:
            _notes.append("Live selected: verify explicit opt-in, redacted secrets, read-only scope where relevant, and no fixture fallback.")
        if dry_run:
            _notes.append("Dry run selected: do not treat this as live proof.")
        if fixture:
            _notes.append("Fixture/mock selected: useful proof, not live proof.")
        if not _notes:
            _notes.append("Data source unknown: ask whether proof was live, mock, fixture, dry-run, static, or unknown.")
        return _label, _reason, _notes, _prompt

    def classification_kind(label: str) -> str:
        if label == "Unsafe or unclear":
            return "danger"
        if label in {"Blocked", "Docs-only", "Audit-only", "Test-only", "Needs follow-up"}:
            return "warn"
        if label == "Implemented and verified":
            return "success"
        return "info"

    return (
        mo,
        read_md,
        split_sections,
        extract_glossary_rows,
        extract_drills,
        extract_answers,
        extract_follow_up,
        drill_category_from_id,
        classify_run,
        classification_kind,
    )


@app.cell
def _(mo):
    header = mo.Html(
        """
        <header class="course-header">
          <h1 class="course-header__title">Coding Agent Supervision 101</h1>
          <div class="course-header__subtitle">
            Reference notebook for supervising coding agents
          </div>
        </header>
        """
    )
    header
    return


@app.cell
def _(mo):
    _section_options = [
        "Start Here",
        "Guided Learning Path",
        "Workbook Practice",
        "Reference Desk",
        "Real Agent Run Triage",
    ]
    mode = mo.ui.tabs(
        {_label: "" for _label in _section_options},
        value="Start Here",
        label="",
    )
    mo.md(f'<nav class="course-nav">{mode}</nav>')
    return (mode,)


# ===== Data loading =====


@app.cell
def _(read_md, split_sections):
    course_sections = split_sections(read_md("course_guide.md"))
    course_section_map = {_t: _b for _t, _b in course_sections}
    return course_section_map, course_sections


@app.cell
def _(extract_glossary_rows, read_md):
    glossary_rows = extract_glossary_rows(read_md("glossary.md"))
    return (glossary_rows,)


@app.cell
def _(drill_category_from_id, extract_drills, read_md):
    _raw_drills = extract_drills(read_md("workbook.md"))
    drills = [
        {**_d, "category": drill_category_from_id(_d["id"])}
        for _d in _raw_drills
    ]
    drill_by_title = {_d["title"]: _d for _d in drills}
    return drill_by_title, drills


@app.cell
def _(extract_answers, read_md):
    answers = extract_answers(read_md("answer_key.md"))
    answer_by_id = {_a["id"]: _a for _a in answers}
    return answer_by_id, answers


@app.cell
def _(read_md):
    quick_reference_md = read_md("quick_reference.md")
    testing_cheat_md = read_md("testing_verification_cheat_sheet.md")
    git_diff_cheat_md = read_md("git_diff_cheat_sheet.md")
    return git_diff_cheat_md, quick_reference_md, testing_cheat_md


# ===== Static structured data =====


@app.cell
def _():
    modules = [
        {
            "id": "1",
            "title": "What a coding agent is actually doing",
            "course_title": "Module 1: What a coding agent is actually doing",
            "objective": "Separate facts, interpretations, and unverified claims in every agent response before trusting it.",
            "what_to_understand": [
                "Activity (files read, commands run) is not the same as progress.",
                "Every claim should be paired with concrete, file-and-command evidence.",
                "A summary is a claim. Evidence is changed files, relevant tests, runtime proof, and explicit limits.",
            ],
            "what_to_ask_next": "Separate facts, interpretations, and unverified claims. Then list the smallest next step that reduces uncertainty.",
            "related_drills": ["5.1", "5.2", "5.5"],
        },
        {
            "id": "2",
            "title": "Terminal and shell basics",
            "course_title": "Module 2: Terminal and shell basics",
            "objective": "Read any shell command as program + subcommand + flags + arguments + target, and ask what it proves.",
            "what_to_understand": [
                "The difference between read-only commands and commands that change files or state.",
                "What success/failure exit codes mean and do not mean.",
                "How env vars and flags change behavior silently.",
            ],
            "what_to_ask_next": "Classify the command: read-only, file-changing, install/build, test, app launch, or live-data-sensitive.",
            "related_drills": ["1.1", "1.2", "1.3", "1.4"],
        },
        {
            "id": "3",
            "title": "Files, paths, and repo structure",
            "course_title": "Module 3: Files, paths, and repo structure",
            "objective": "Recognize what a changed file path implies about whether runtime behavior could have changed.",
            "what_to_understand": [
                "`src/` vs `tests/` vs `docs/` vs `scripts/` vs `.env` vs `.state` and what each implies.",
                "Docs-only diffs do not change runtime behavior.",
                "A test diff without a matching source diff is usually test-only.",
            ],
            "what_to_ask_next": "Classify every changed file as source, test, docs, config, script, generated state, or unknown.",
            "related_drills": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        },
        {
            "id": "4",
            "title": "Git fundamentals",
            "course_title": "Module 4: Git fundamentals",
            "objective": "Use Git output to verify what changed, what is committed, and what is still in flight.",
            "what_to_understand": [
                "Working tree vs staged vs unstaged vs untracked.",
                "Branch, commit hash, pushed vs local.",
                "A clean tree does not prove the app works.",
            ],
            "what_to_ask_next": "Show the current branch, final git status, whether work is committed, commit hash if any, and whether the commit is pushed or local.",
            "related_drills": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8"],
        },
        {
            "id": "5",
            "title": "Tests and verification",
            "course_title": "Module 5: Tests and verification",
            "objective": "Know what a passing test proves and, more importantly, what it does NOT prove.",
            "what_to_understand": [
                "Focused test vs full suite vs build vs smoke vs live smoke.",
                "Skipped tests are not passing tests.",
                "Build success is not test success.",
            ],
            "what_to_ask_next": "List exact test commands, pass/fail/skip counts, and what each command proves. Also state what these tests do not prove.",
            "related_drills": ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"],
        },
        {
            "id": "6",
            "title": "Runtime and launch concepts",
            "course_title": "Module 6: Runtime and launch concepts",
            "objective": "Recognize that 'the app started' is not the same as 'the feature works'.",
            "what_to_understand": [
                "A launch URL only proves a process bound a port.",
                "Operator workflow exercise is the highest verification rung.",
                "Dry-run is not live.",
            ],
            "what_to_ask_next": "Show the exact operator-visible behavior change and the exact action a person would take to exercise it.",
            "related_drills": ["1.5", "1.6", "3.5"],
        },
        {
            "id": "7",
            "title": "Reading coding-agent prompts",
            "course_title": "Module 7: Reading coding-agent prompts",
            "objective": "Tell a strong, scoped prompt from a vague one before sending it.",
            "what_to_understand": [
                "A strong prompt names goal, scope, constraints, acceptance criteria, safety boundaries, and verification commands.",
                "Vague prompts encourage audit-only and busywork responses.",
                "Constraints prevent drift.",
            ],
            "what_to_ask_next": "Rewrite the request with explicit scope, constraints, acceptance criteria, and verification commands.",
            "related_drills": [],
        },
        {
            "id": "8",
            "title": "Reading coding-agent output",
            "course_title": "Module 8: Reading coding-agent output",
            "objective": "Read a final agent response as an evidence package — and notice what is missing.",
            "what_to_understand": [
                "An evidence package lists changed files, commands, test results, what now works, what was not verified, blockers, git state, and data source.",
                "Vague endings (\"Done. All tests pass.\") are not evidence.",
                "Missing fields are signal.",
            ],
            "what_to_ask_next": "List changed files, exact commands, test results, what now works, what was not verified, blockers, and Git state.",
            "related_drills": ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10"],
        },
        {
            "id": "9",
            "title": "Live data and safety",
            "course_title": "Module 9: Live data and safety",
            "objective": "Distinguish a real live-data proof from fixture, mock, or dry-run output.",
            "what_to_understand": [
                "Live proof requires explicit opt-in, redacted output, no fixture fallback, and read-only scope where possible.",
                "Fixture and dry-run results are useful, but they are not live proof.",
                "Secrets must never appear in output.",
            ],
            "what_to_ask_next": "Label each verification command as mock, fixture, dry-run, or live. If live, show the opt-in command, redacted output, and whether fixture fallback was impossible.",
            "related_drills": ["1.7", "4.7", "4.8", "5.7", "5.8"],
        },
        {
            "id": "10",
            "title": "Supervising the build loop",
            "course_title": "Module 10: Supervising the build loop",
            "objective": "After every agent run, ask the same fixed questions before moving on.",
            "what_to_understand": [
                "What changed, which files, which commands, what was proven, what was not verified, what is blocked, and what the next concrete step is.",
                "A regular cadence beats hero supervision.",
                "The triage form is meant to be re-used after every run.",
            ],
            "what_to_ask_next": "What changed, which files changed, which commands ran, what did each prove, what was not verified, what is the next concrete implementation step?",
            "related_drills": ["5.1", "5.5", "5.10"],
        },
    ]
    module_by_title = {_m["title"]: _m for _m in modules}
    return module_by_title, modules


@app.cell
def _():
    drill_extras = {
        "1.1": {
            "mistake": "Reading a clean `git status` as proof that the app works.",
            "follow_up": "What command actually proves the operator workflow runs, beyond status?",
        },
        "1.2": {
            "mistake": "Treating one passing test file as proof the whole app works.",
            "follow_up": "Did the app launch and exercise the operator path this test covers?",
        },
        "1.3": {
            "mistake": "Calling a successful build proof that the feature works.",
            "follow_up": "Did anyone open the built bundle and exercise the target workflow in a browser?",
        },
        "1.4": {
            "mistake": "Treating a 200 on `/health` as proof the operator path works.",
            "follow_up": "Beyond `/health`, which exact endpoint serves the operator workflow, and what did it return?",
        },
        "1.5": {
            "mistake": "Calling a dry-run path a launch.",
            "follow_up": "What does a non-dry-run launch look like, and was it actually run?",
        },
        "1.6": {
            "mistake": "Server started is not the same as target screen tested.",
            "follow_up": "Which exact URL on the dev server exercises the feature, and was it opened?",
        },
        "1.7": {
            "mistake": "Assuming live mode without checking that output shows opt_in_live=yes and no fallback.",
            "follow_up": "Show the live output: explicit opt-in, redacted secrets, quote received, no fixture fallback.",
        },
        "1.8": {
            "mistake": "Treating a grep result as proof that the fallback is safe.",
            "follow_up": "For each match, read the surrounding code and explain when the fallback actually triggers.",
        },
        "1.9": {
            "mistake": "Forgetting that `git diff` hides staged changes by default.",
            "follow_up": "Show both the staged and unstaged diffs for this file.",
        },
        "1.10": {
            "mistake": "Treating a fixture run as live-data proof.",
            "follow_up": "Was any live provider exercised, or is this only fixture data?",
        },
        "2.1": {
            "mistake": "Treating an untracked test file as if it were already in the commit.",
            "follow_up": "Should the new test be committed, ignored, or left as scratch?",
        },
        "2.2": {
            "mistake": "Assuming the next commit captures the whole file because the path appears in `git status`.",
            "follow_up": "Show the staged diff and the unstaged diff separately.",
        },
        "2.3": {
            "mistake": "Reading a clean tree as proof that the app works.",
            "follow_up": "What runtime check actually confirms the feature works on this branch?",
        },
        "2.4": {
            "mistake": "Treating 'on main' as the right branch by default.",
            "follow_up": "Is direct-to-main expected here, or should this be a feature branch?",
        },
        "2.5": {
            "mistake": "Trusting commit messages as evidence of behavior change.",
            "follow_up": "Show `git show --stat <hash>` for the top commit and the verification command that exercises it.",
        },
        "2.6": {
            "mistake": "Treating a mixed-type diff stat as proof of real implementation.",
            "follow_up": "For the source file in this diff, which test exercises the change?",
        },
        "2.7": {
            "mistake": "Treating a created commit as a passing implementation.",
            "follow_up": "Was the commit pushed, and did focused tests pass before the commit?",
        },
        "2.8": {
            "mistake": "Assuming the work is shared because the tree is clean.",
            "follow_up": "Was the commit pushed, or is it local only?",
        },
        "3.1": {
            "mistake": "Assuming a renderer diff implements the feature without confirming the function is on the active UI path.",
            "follow_up": "Show that `render_manual_query` is actually called by the operator-facing cockpit.",
        },
        "3.2": {
            "mistake": "Treating a new test as the implementation.",
            "follow_up": "What source change makes this test pass, and did the test fail before the implementation landed?",
        },
        "3.3": {
            "mistake": "Treating a docs update as a runtime change.",
            "follow_up": "Which runtime file enforces the safety rule described in these docs?",
        },
        "3.4": {
            "mistake": "Adding an npm script is not the same as running it.",
            "follow_up": "Run `npm run smoke` and show the actual output.",
        },
        "3.5": {
            "mistake": "Adding a dry-run flag is not the same as exercising a real launch.",
            "follow_up": "Show both `--dry-run` output and a real launch, or explicitly state that real launch was not exercised.",
        },
        "4.1": {
            "mistake": "Calling one passing test file a green build.",
            "follow_up": "What broader suite or runtime smoke would expose a regression beyond this file?",
        },
        "4.2": {
            "mistake": "Disabling or deleting a failing test to make CI green.",
            "follow_up": "Is the failing test correct? If yes, fix the code. If no, fix the test and explain why.",
        },
        "4.3": {
            "mistake": "Counting skipped tests as passing.",
            "follow_up": "List each skipped test and the reason it was skipped.",
        },
        "4.4": {
            "mistake": "Full-suite green is not the same as the feature working.",
            "follow_up": "Which test in the suite exercises this feature, and what does it verify?",
        },
        "4.5": {
            "mistake": "Treating a successful build as 'tests passed'.",
            "follow_up": "Run the focused tests for the changed area and show the output.",
        },
        "4.6": {
            "mistake": "Conflating a fixture pass with live-data proof.",
            "follow_up": "Show a live or dry-run smoke that complements this fixture pass.",
        },
        "4.7": {
            "mistake": "Reading dry-run output as live confirmation.",
            "follow_up": "What is the smallest bounded live smoke that would actually exercise the path?",
        },
        "4.8": {
            "mistake": "Stopping at a single live quote and calling the feature done.",
            "follow_up": "What broader live coverage is still missing, and what is the safest next live step?",
        },
        "5.1": {
            "mistake": "Trusting an evidence-rich summary without confirming the renderer is on the runtime path.",
            "follow_up": "Show that the modified renderer is wired into the active cockpit and exercised at runtime.",
        },
        "5.2": {
            "mistake": "Accepting 'Done. All tests pass.' as evidence.",
            "follow_up": "List changed files, exact commands, test results, what now works, what was not verified, blockers, and Git state.",
        },
        "5.3": {
            "mistake": "Treating docs changes as runtime implementation.",
            "follow_up": "Which runtime file would have to change to actually enforce the live-data safety rule?",
        },
        "5.4": {
            "mistake": "Treating a failing test addition as completed work.",
            "follow_up": "Implement the smallest source change that makes the test pass without weakening the test.",
        },
        "5.5": {
            "mistake": "Accepting an inspection report as the implementation.",
            "follow_up": "Implement the recommended change now and add a focused test, unless you are blocked. If blocked, name the exact blocker.",
        },
        "5.6": {
            "mistake": "Calling work blocked when source/tests already changed and focused tests passed.",
            "follow_up": "Confirm secrets stayed protected and that the changed provider factory is on the launch path.",
        },
        "5.7": {
            "mistake": "Treating fixture-quote tests as live verification.",
            "follow_up": "Either run a bounded live smoke or restate the result as fixture-only.",
        },
        "5.8": {
            "mistake": "Stopping at a bounded live smoke without checking the broader operator path.",
            "follow_up": "Does this live smoke exercise the actual app runtime, or only a standalone harness?",
        },
        "5.9": {
            "mistake": "Calling a rename or reorder a 'safe' change without running tests.",
            "follow_up": "Run the affected tests and show what behavior actually changed.",
        },
        "5.10": {
            "mistake": "Trusting a commit hash and a clean tree as proof the feature works.",
            "follow_up": "Show changed files, verification commands, pushed/local status, and the operator behavior that now works.",
        },
    }
    category_default_mistake = {
        "Command dissection": "Treating command success as proof the operator workflow works.",
        "Git output": "Treating Git state (clean tree, new commit) as proof of behavior change.",
        "Diff reading": "Reading any diff as implementation without checking the runtime path.",
        "Test output": "Treating a passing test as proof the whole app works.",
        "Agent-summary triage": "Trusting the headline of an agent summary without checking the evidence.",
    }
    return category_default_mistake, drill_extras


@app.cell
def _():
    drill_categories = [
        "Command dissection",
        "Git output",
        "Diff reading",
        "Test output",
        "Agent-summary triage",
    ]
    return (drill_categories,)


@app.cell
def _():
    command_examples = {
        "git status --short": {
            "program": "`git` — the version-control tool.",
            "subcommand": "`status` — report the working-tree state.",
            "flags": "`--short` — one compact line per file.",
            "arguments": "(none)",
            "target": "Current repo working tree.",
            "proves": "Which files are modified, staged, or untracked right now.",
            "does_not_prove": "That the app actually works, or that anything was committed.",
        },
        "uv run pytest -q tests/test_runtime_gate.py": {
            "program": "`uv` — runs the next program inside the project environment.",
            "subcommand": "`run pytest` — uv invokes `pytest`, the test runner.",
            "flags": "`-q` — quiet output (no per-test verbosity).",
            "arguments": "(none beyond the target)",
            "target": "`tests/test_runtime_gate.py` — a single test file.",
            "proves": "The collected tests in that one file passed or failed.",
            "does_not_prove": "App launch, browser UI, or live data.",
        },
        "curl -s -o /dev/null -w '%{http_code}\\n' http://localhost:8000/api/health": {
            "program": "`curl` — make an HTTP request.",
            "subcommand": "(none)",
            "flags": "`-s` silent · `-o /dev/null` discard body · `-w '%{http_code}\\n'` print only the status code.",
            "arguments": "(none beyond the target URL)",
            "target": "`http://localhost:8000/api/health` — a local health endpoint.",
            "proves": "The endpoint replied with an HTTP status code.",
            "does_not_prove": "That the full operator workflow works, or that data is correct.",
        },
        "SCHWAB_API_KEY=*** uv run python scripts/run_live_smoke.py --opt-in-live --symbol SPY --max-calls 1 --read-only": {
            "program": "`uv run python` — run a Python script inside the project env.",
            "subcommand": "(none)",
            "flags": "`--opt-in-live` requires explicit live mode · `--max-calls 1` bounds the request count · `--read-only` forbids mutation.",
            "arguments": "`--symbol SPY` — the only symbol allowed for this run.",
            "target": "`scripts/run_live_smoke.py`, with a redacted env var supplying credentials.",
            "proves": "If output confirms live mode, one quote, no fallback, and no secret leak — a bounded read-only live call ran.",
            "does_not_prove": "Broader live coverage, multi-symbol behavior, or write-path safety.",
        },
    }
    return (command_examples,)


# ===== UI controls =====


@app.cell
def _(mo, modules):
    _titles = [_m["title"] for _m in modules]
    module_selector = mo.ui.dropdown(
        options=_titles,
        value=_titles[0] if _titles else None,
        label="Module",
    )
    return (module_selector,)


@app.cell
def _(drill_categories, mo):
    drill_category = mo.ui.radio(
        options=drill_categories,
        value=drill_categories[0],
        label="Drill category",
        inline=True,
    )
    return (drill_category,)


@app.cell
def _(drill_category, drills, mo):
    _filtered = [_d["title"] for _d in drills if _d["category"] == drill_category.value]
    drill_selector = mo.ui.dropdown(
        options=_filtered,
        value=_filtered[0] if _filtered else None,
        label="Drill",
    )
    return (drill_selector,)


@app.cell
def _(mo):
    show_answer = mo.ui.checkbox(label="Reveal answer and follow-up", value=False)
    return (show_answer,)


@app.cell
def _(mo):
    reference_sub = mo.ui.dropdown(
        options=[
            "Glossary",
            "Command anatomy",
            "Quick reference",
            "Testing & verification cheat sheet",
            "Git & diff cheat sheet",
        ],
        value="Glossary",
        label="Reference",
    )
    return (reference_sub,)


@app.cell
def _(glossary_rows, mo):
    _categories = ["All"] + sorted({_r["category"] for _r in glossary_rows})
    glossary_category = mo.ui.dropdown(
        options=_categories,
        value="All",
        label="Category",
    )
    glossary_search = mo.ui.text(
        label="Search",
        placeholder="term, definition, or topic",
        full_width=True,
    )
    return glossary_category, glossary_search


@app.cell
def _(command_examples, mo):
    command_selector = mo.ui.dropdown(
        options=list(command_examples),
        value=list(command_examples)[0],
        label="Command",
    )
    return (command_selector,)


@app.cell
def _(mo):
    summary = mo.ui.text_area(
        label="Agent summary",
        placeholder="Paste the agent's final response.",
        rows=7,
        full_width=True,
    )
    files = mo.ui.text_area(
        label="Changed files (one per line)",
        placeholder="src/cockpit/manual_query.py\ntests/test_manual_query.py",
        rows=5,
        full_width=True,
    )
    commands = mo.ui.text_area(
        label="Commands and test output",
        placeholder="uv run pytest -q tests/test_manual_query.py\n7 passed",
        rows=5,
        full_width=True,
    )
    source_changed = mo.ui.checkbox(label="Source changed")
    tests_changed = mo.ui.checkbox(label="Tests changed")
    docs_only = mo.ui.checkbox(label="Docs-only")
    test_only = mo.ui.checkbox(label="Test-only")
    audit_only = mo.ui.checkbox(label="Audit-only")
    app_launched = mo.ui.checkbox(label="App launched / workflow exercised")
    dry_run = mo.ui.checkbox(label="Dry-run used")
    fixture = mo.ui.checkbox(label="Fixture or mock used")
    live = mo.ui.checkbox(label="Live mode or live data claimed")
    blocked = mo.ui.checkbox(label="Blocked")
    unsafe = mo.ui.checkbox(label="Unsafe or unclear")
    return (
        app_launched,
        audit_only,
        blocked,
        commands,
        docs_only,
        dry_run,
        files,
        fixture,
        live,
        source_changed,
        summary,
        test_only,
        tests_changed,
        unsafe,
    )


# ===== Main render =====


@app.cell
def _(
    answer_by_id,
    app_launched,
    audit_only,
    blocked,
    category_default_mistake,
    classification_kind,
    classify_run,
    command_examples,
    command_selector,
    commands,
    course_section_map,
    docs_only,
    drill_by_title,
    drill_category,
    drill_extras,
    drill_selector,
    drills,
    dry_run,
    extract_follow_up,
    files,
    fixture,
    git_diff_cheat_md,
    glossary_category,
    glossary_rows,
    glossary_search,
    live,
    mo,
    mode,
    module_by_title,
    module_selector,
    modules,
    quick_reference_md,
    reference_sub,
    show_answer,
    source_changed,
    summary,
    test_only,
    tests_changed,
    unsafe,
):
    _mode = mode.value

    if _mode == "Start Here":
        main_panel = mo.vstack(
            [
                mo.md("## Start Here"),
                mo.md(
                    "This page tells you what the app is for, the four ways to use it, "
                    "and a concrete first session you can finish in thirty minutes."
                ),
                mo.callout(
                    mo.md(
                        "**Core rule.** A coding agent's summary is a *claim*. "
                        "Your job is to compare the claim against evidence — changed files, "
                        "commands run, tests, runtime, and Git state — before trusting it."
                    ),
                    kind="info",
                ),
                mo.md("### What this course is for"),
                mo.md(
                    "You are supervising a coding agent in a real repository. You may not write "
                    "production code yourself, but you decide when to trust the agent's report, "
                    "when to challenge it, and what to ask next. This notebook is the reference "
                    "and practice surface for that work."
                ),
                mo.md("### Four ways to use this app"),
                mo.md(
                    "- **Guided Learning Path** — read the course one module at a time, with an "
                    "objective, examples, and pointers to matching workbook drills.\n"
                    "- **Workbook Practice** — pick a drill, attempt the answer yourself, then "
                    "reveal the intended interpretation, the common mistake, and the best follow-up prompt.\n"
                    "- **Reference Desk** — look up glossary terms, command anatomy, the quick "
                    "reference, and cheat sheets without losing your place in the course.\n"
                    "- **Real Agent Run Triage** — after every real agent run, paste the summary "
                    "and use the form to classify what was actually proven."
                ),
                mo.md("### How to use the workbook"),
                mo.md(
                    "For every drill, before you reveal the answer, work through these four "
                    "questions in your head or on paper:"
                ),
                mo.callout(
                    mo.md(
                        "1. **What is directly visible?** (file paths, commands, output, exit codes)\n"
                        "2. **What is a reasonable interpretation?** (what this evidence probably means)\n"
                        "3. **What cannot be safely concluded?** (the leap the agent might invite you to make)\n"
                        "4. **What should I ask next?** (the narrow prompt that reduces uncertainty)"
                    ),
                    kind="neutral",
                ),
                mo.md("### What to do after every coding-agent run"),
                mo.md(
                    "Open **Real Agent Run Triage**. Paste the agent's final summary, list the "
                    "changed files, paste the commands run, and toggle the flags that match the "
                    "run. The form classifies the result and suggests the next prompt."
                ),
                mo.callout(
                    mo.md(
                        "**Recommended path for first-time learners.**\n"
                        "1. Read this *Start Here* page.\n"
                        "2. Open **Guided Learning Path** and read Module 1.\n"
                        "3. Open **Workbook Practice**, *Command dissection*, **Drill 1.1**.\n"
                        "4. Work the four questions, then reveal the answer.\n"
                        "5. Open **Real Agent Run Triage** with a real agent summary you have on hand."
                    ),
                    kind="success",
                ),
                mo.md("### 30-minute first session"),
                mo.md(
                    "| Minutes | Do |\n"
                    "|---|---|\n"
                    "| 0 – 5 | Read this page in full. |\n"
                    "| 5 – 15 | Guided Learning Path → Module 1 → read objective, body, and \"what to ask next\". |\n"
                    "| 15 – 22 | Workbook Practice → Command dissection → Drills 1.1 and 1.2. Reveal answers. |\n"
                    "| 22 – 30 | Real Agent Run Triage → paste a real (or recent) agent summary and read the classification. |"
                ),
                mo.md("### 7-day practice plan"),
                mo.md(
                    "| Day | Focus |\n"
                    "|---|---|\n"
                    "| 1 | Module 1 + Drills 5.1, 5.2, 5.5. |\n"
                    "| 2 | Module 2 + Drills 1.1 – 1.4. |\n"
                    "| 3 | Module 3 + Drills 3.1 – 3.5. |\n"
                    "| 4 | Module 4 + Drills 2.1 – 2.8. |\n"
                    "| 5 | Module 5 + Drills 4.1 – 4.6. |\n"
                    "| 6 | Module 8 + Drills 5.1 – 5.10. |\n"
                    "| 7 | Module 9 + Drills 1.7, 4.7, 4.8, 5.7, 5.8. Run triage on three real agent sessions. |"
                ),
            ]
        )

    elif _mode == "Guided Learning Path":
        _module = module_by_title.get(module_selector.value) or modules[0]
        _body = course_section_map.get(_module["course_title"], "Module body not found.")
        _understand_md = "\n".join(f"- {_x}" for _x in _module["what_to_understand"])
        _related_titles = []
        for _did in _module["related_drills"]:
            _match = next((_d for _d in drills if _d["id"] == _did), None)
            if _match:
                _related_titles.append(_match["title"])
        _related_md = (
            "\n".join(f"- {_t}" for _t in _related_titles)
            if _related_titles
            else "_No drills mapped to this module yet._"
        )
        main_panel = mo.vstack(
            [
                mo.md("## Guided Learning Path"),
                mo.md(
                    "Read the course one module at a time. Each module has an objective, the "
                    "body content, what you should understand before moving on, what to ask the "
                    "coding agent next, and which workbook drills to practice."
                ),
                module_selector,
                mo.callout(
                    mo.md(f"**Objective.** {_module['objective']}"),
                    kind="info",
                ),
                mo.md("### Module content"),
                mo.md(_body),
                mo.md("### What you should understand before moving on"),
                mo.md(_understand_md),
                mo.callout(
                    mo.md(
                        "**What to ask the coding agent next.**\n\n"
                        f"```text\n{_module['what_to_ask_next']}\n```"
                    ),
                    kind="success",
                ),
                mo.md("### Related workbook drills"),
                mo.md(_related_md),
                mo.callout(
                    mo.md(
                        "Open **Workbook Practice**, pick the matching category, and find these "
                        "drills by ID."
                    ),
                    kind="neutral",
                ),
            ]
        )

    elif _mode == "Workbook Practice":
        _drill = drill_by_title.get(drill_selector.value) if drill_selector.value else None
        _items = [
            mo.md("## Workbook Practice"),
            mo.md(
                "Pick a category, pick a drill, answer the four questions in your head or on "
                "paper, then reveal the intended interpretation, the common mistake, and the "
                "best follow-up prompt."
            ),
            mo.callout(
                mo.md(
                    "**How to answer this drill.**\n\n"
                    "1. What is directly visible?\n"
                    "2. What is a reasonable interpretation?\n"
                    "3. What cannot be safely concluded?\n"
                    "4. What should I ask next?"
                ),
                kind="neutral",
            ),
            drill_category,
            mo.hstack([drill_selector, show_answer], justify="start", gap=1.0),
        ]
        if _drill is None:
            _items.append(
                mo.callout(
                    mo.md("No drill selected. Pick a category and drill above."),
                    kind="warn",
                )
            )
        else:
            _items.append(mo.md(_drill["body"]))
            if show_answer.value:
                _answer = answer_by_id.get(_drill["id"])
                if _answer:
                    _items.append(
                        mo.callout(mo.md(_answer["body"]), kind="success")
                    )
                else:
                    _items.append(
                        mo.callout(
                            mo.md(
                                "No matching answer was found in the answer key. Open "
                                "**Reference Desk → Quick reference** for the general triage rubric."
                            ),
                            kind="warn",
                        )
                    )
                _extra = drill_extras.get(_drill["id"], {})
                _mistake = _extra.get("mistake") or category_default_mistake.get(
                    _drill["category"],
                    "Common mistake: treating evidence as proof — compare claim to file/command output.",
                )
                _items.append(
                    mo.callout(
                        mo.md(f"**Common mistaken conclusion.** {_mistake}"),
                        kind="warn",
                    )
                )
                _follow_up = _extra.get("follow_up")
                if not _follow_up and _answer:
                    _follow_up = extract_follow_up(_answer["body"])
                if not _follow_up:
                    _follow_up = (
                        "List changed files, exact commands, test results, what now works, what was "
                        "not verified, blockers, and Git state."
                    )
                _items.append(
                    mo.callout(
                        mo.md(
                            f"**Best follow-up prompt.**\n\n```text\n{_follow_up}\n```"
                        ),
                        kind="info",
                    )
                )
            else:
                _items.append(
                    mo.callout(
                        mo.md(
                            "Answer hidden. Work the four questions above, then toggle "
                            "**Reveal answer and follow-up**."
                        ),
                        kind="neutral",
                    )
                )
        main_panel = mo.vstack(_items)

    elif _mode == "Reference Desk":
        _items = [
            mo.md("## Reference Desk"),
            mo.md(
                "Fast lookup while you supervise real agents. Switch between glossary, command "
                "anatomy, the quick reference, and the cheat sheets."
            ),
            reference_sub,
        ]
        _sub = reference_sub.value
        if _sub == "Glossary":
            import html as _html

            CATEGORY_COLOR = {
                "Terminal and shell": "teal",
                "Files and paths": "blue",
                "Git": "orange",
                "Repo structure": "blue",
                "Tests": "gold",
                "App runtime": "teal",
                "Coding agents": "purple",
                "Live data and safety": "orange",
                "Orchestration prompts": "gold",
            }
            _query = (glossary_search.value or "").lower().strip()
            _filtered = []
            for _row in glossary_rows:
                if glossary_category.value != "All" and _row["category"] != glossary_category.value:
                    continue
                if _query and _query not in " ".join(_row.values()).lower():
                    continue
                _filtered.append(_row)
            _cards = []
            for _r in _filtered:
                _color = CATEGORY_COLOR.get(_r["category"], "teal")
                _cards.append(
                    f"""
                    <article class="glossary-card glossary-card--{_color}">
                      <h3 class="glossary-card__term">{_html.escape(_r["term"])}</h3>
                      <div class="glossary-card__category">{_html.escape(_r["category"])}</div>
                      <div class="glossary-card__body">{_html.escape(_r["definition"])}</div>
                      <div class="glossary-card__meta">
                        <strong>Why you see it:</strong> {_html.escape(_r["why_seen"])}
                      </div>
                      <div class="glossary-card__meta">
                        <strong>What to ask:</strong> {_html.escape(_r["ask"])}
                      </div>
                    </article>
                    """
                )
            _glossary_cards = mo.Html(
                '<div class="glossary-vstack">' + "\n".join(_cards[:75]) + "</div>"
            )
            _items.extend(
                [
                    mo.md("### Glossary"),
                    mo.hstack(
                        [glossary_category, glossary_search],
                        justify="start",
                        widths=[0, 1],
                        gap=1.0,
                    ),
                    mo.md(f"**{len(_filtered)}** entries shown."),
                    _glossary_cards,
                ]
            )
        elif _sub == "Command anatomy":
            _detail = command_examples[command_selector.value]
            _rows = "\n".join(
                f"| {_label} | {_detail[_key]} |"
                for _label, _key in [
                    ("Program", "program"),
                    ("Subcommand", "subcommand"),
                    ("Flags", "flags"),
                    ("Arguments", "arguments"),
                    ("Target", "target"),
                    ("Proves", "proves"),
                    ("Does not prove", "does_not_prove"),
                ]
            )
            _items.extend(
                [
                    mo.md("### Command anatomy"),
                    mo.md(
                        "Pick a real command. The breakdown explains program, subcommand, "
                        "flags, arguments, target, and what the command actually proves."
                    ),
                    command_selector,
                    mo.md(f"```bash\n{command_selector.value}\n```"),
                    mo.md("| Part | Meaning |\n|---|---|\n" + _rows),
                ]
            )
        elif _sub == "Quick reference":
            _items.append(mo.md(quick_reference_md))
        elif _sub == "Testing & verification cheat sheet":
            _items.append(mo.md(testing_cheat_md))
        elif _sub == "Git & diff cheat sheet":
            _items.append(mo.md(git_diff_cheat_md))
        main_panel = mo.vstack(_items)

    elif _mode == "Real Agent Run Triage":
        _label, _reason, _notes, _prompt = classify_run(
            summary.value or "",
            files.value or "",
            commands.value or "",
            bool(source_changed.value),
            bool(tests_changed.value),
            bool(app_launched.value),
            bool(live.value),
            bool(dry_run.value),
            bool(fixture.value),
            bool(docs_only.value),
            bool(test_only.value),
            bool(audit_only.value),
            bool(blocked.value),
            bool(unsafe.value),
        )
        _notes_md = "\n".join(f"- {_n}" for _n in _notes)
        LABEL_KIND = {
            "Implemented and verified": "success",
            "Implemented but not runtime-verified": "warn",
            "Implemented but not verified": "warn",
            "Test-only": "info",
            "Needs follow-up": "info",
            "Blocked": "danger",
            "Unsafe or unclear": "danger",
        }
        _kind = LABEL_KIND.get(_label, "info")
        import html as _html
        import json as _json

        _prompt_html = _html.escape(_prompt)
        _prompt_js = _json.dumps(_prompt).replace("</", "<\\/")
        _prompt_srcdoc = f"""
        <!doctype html>
        <html>
          <head>
            <style>
              :root {{
                --panel-dark: #1c1b19;
                --accent-teal: #01696f;
                --text-primary-dark: #ffffff;
                --text-secondary: #797876;
                --text-code: #e6e5e2;
                --border-subtle: oklch(1 0 0 / 0.08);
                --radius-card: 8px;
                --radius-button: 6px;
                --font-body: "Satoshi", system-ui, sans-serif;
                --font-mono: ui-monospace, "JetBrains Mono", "Menlo", monospace;
                --text-sm: 14px;
              }}
              html,
              body {{
                background: transparent;
                margin: 0;
              }}
              :focus-visible {{
                outline: 2px solid var(--accent-teal);
                outline-offset: 2px;
              }}
              .next-prompt-card {{
                background: var(--panel-dark);
                border: 1px solid var(--border-subtle);
                border-radius: var(--radius-card);
                box-sizing: border-box;
                min-height: 92px;
                padding: 16px;
                position: relative;
              }}
              .next-prompt-card__copy {{
                background: transparent;
                border: 1px solid var(--border-subtle);
                border-radius: var(--radius-button);
                color: var(--text-secondary);
                cursor: pointer;
                font-family: var(--font-body);
                font-size: var(--text-sm);
                font-weight: 500;
                line-height: 1.3;
                padding: 6px 12px;
                position: absolute;
                right: 16px;
                top: 16px;
                transition: color 120ms ease, border-color 120ms ease;
              }}
              .next-prompt-card__copy:hover {{
                border-color: var(--accent-teal);
                color: var(--text-primary-dark);
              }}
              .next-prompt-card__text {{
                color: var(--text-code);
                font-family: var(--font-mono);
                font-size: var(--text-sm);
                line-height: 1.55;
                margin: 36px 0 0;
                white-space: pre-wrap;
              }}
            </style>
          </head>
          <body>
            <section class="next-prompt-card">
              <button class="next-prompt-card__copy" type="button">Copy</button>
              <pre class="next-prompt-card__text">{_prompt_html}</pre>
            </section>
            <script>
              const btn = document.querySelector('.next-prompt-card__copy');
              const promptText = {_prompt_js};
              btn.addEventListener('click', async () => {{
                try {{
                  await navigator.clipboard.writeText(promptText);
                }} catch (e) {{
                  const ta = document.createElement('textarea');
                  ta.value = promptText;
                  document.body.appendChild(ta);
                  ta.select();
                  document.execCommand('copy');
                  document.body.removeChild(ta);
                }}
                btn.textContent = 'Copied';
                setTimeout(() => btn.textContent = 'Copy', 1200);
              }});
            </script>
          </body>
        </html>
        """
        _prompt_srcdoc_attr = _html.escape(_prompt_srcdoc, quote=True)
        _next_prompt_card = mo.Html(
            f"""
            <iframe
              class="next-prompt-frame"
              title="Next prompt"
              allow="clipboard-write"
              srcdoc="{_prompt_srcdoc_attr}"
            ></iframe>
            """
        )
        _verification_panel = mo.md(
            f"""
            <section class="triage-panel">
              <div class="triage-panel__label">Verification evidence</div>
              <div class="triage-panel__row">
                {app_launched}
                {live}
                {dry_run}
                {fixture}
              </div>
            </section>
            """
        )
        _risk_panel = mo.md(
            f"""
            <section class="triage-panel">
              <div class="triage-panel__label">Risk flags</div>
              <div class="triage-panel__row">
                {docs_only}
                {audit_only}
                {blocked}
                {unsafe}
              </div>
            </section>
            """
        )
        main_panel = mo.vstack(
            [
                mo.md("## Real Agent Run Triage"),
                mo.md(
                    "Use this after every real agent run. Paste the agent's summary, list "
                    "changed files, paste the commands run, then toggle the flags that match the "
                    "run. The classification updates live."
                ),
                summary,
                files,
                commands,
                mo.md("**What changed**"),
                mo.hstack(
                    [source_changed, tests_changed, test_only],
                    justify="start",
                    gap=1.0,
                    wrap=True,
                ),
                mo.vstack([_verification_panel, _risk_panel], gap=1.0),
                mo.callout(
                    mo.md(
                        f"### Classification: {_label}\n\n"
                        f"**Reason.** {_reason}\n\n"
                        f"**Data-source notes.**\n{_notes_md}"
                    ),
                    kind=_kind,
                ),
                _next_prompt_card,
            ]
        )

    else:
        main_panel = mo.md("Pick a mode above.")

    main_panel
    return


if __name__ == "__main__":
    app.run()
