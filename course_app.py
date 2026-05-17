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
            _drills.append((f"Drill {_match.group(1).strip()}", _workbook_body[_start:_end].strip()))
        return _drills

    def extract_answers(markdown_text: str):
        _matches = list(re.finditer(r"^### Answer\s+([^\n]+)\n", markdown_text, re.MULTILINE))
        _answers = []
        for _index, _match in enumerate(_matches):
            _start = _match.start()
            _end = _matches[_index + 1].start() if _index + 1 < len(_matches) else len(markdown_text)
            _answers.append((f"Answer {_match.group(1).strip()}", markdown_text[_start:_end].strip()))
        return _answers

    def classify_run(summary, files, commands, app_launched, live, dry_run, fixture, docs_only, audit_only, blocked, unsafe):
        _changed = [_line.strip() for _line in files.splitlines() if _line.strip()]
        _text = "\n".join([summary, files, commands]).lower()
        _has_source = any(
            _path.startswith(("src/", "app/", "scripts/")) or _path in {"package.json", "pyproject.toml"}
            for _path in _changed
        )
        _has_tests = "test" in _text or any("test" in _path for _path in _changed)
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
        elif docs_only or (_changed and all(_path.endswith(".md") or _path.startswith("docs/") for _path in _changed)):
            _label = "Docs-only"
            _reason = "Only documentation-style files are listed, so runtime behavior is not proven changed."
            _prompt = "Do not call this implemented. Identify the source/config/script file that would have to change to affect runtime behavior."
        elif _has_source and _has_tests and (app_launched or live or dry_run or _has_pass):
            _label = "Implemented and verified" if app_launched or live else "Implemented but not runtime-verified"
            _reason = "Source/config/script changes and verification evidence are present. Runtime/live proof depends on the selected verification source."
            _prompt = "List exact changed runtime files, exact verification commands, what each command proved, and what was not verified."
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
        if label in {"Unsafe or unclear"}:
            return "danger"
        if label in {"Blocked", "Docs-only", "Audit-only", "Test-only", "Needs follow-up"}:
            return "warn"
        if label in {"Implemented and verified"}:
            return "success"
        return "info"

    return (
        mo,
        read_md,
        split_sections,
        extract_glossary_rows,
        extract_drills,
        extract_answers,
        classify_run,
        classification_kind,
    )


@app.cell
def _(mo):
    header = mo.md(
        """
        # Coding Agent Supervision 101

        A reference-first notebook for non-developers supervising coding agents in real repositories.
        Pick a section below, work through drills, and use the triage form after every agent run.
        """
    )
    header
    return


@app.cell
def _(mo):
    orientation = mo.vstack(
        [
            mo.md(
                """
                ## How to use this app

                - **Course guide** — reading material, organized by module.
                - **Glossary** — fast lookup for terms you see in agent output.
                - **Workbook drills** — practice reading agent output; reveal the answer when ready.
                - **Answer key** — intended supervisor interpretation for each drill.
                - **Quick reference** — one-page cheat sheet for after an agent finishes.
                - **Command anatomy** — shell commands broken down word by word.
                - **Agent-output triage** — paste the agent's final response and classify the run.
                """
            ),
            mo.callout(
                mo.md(
                    """
                    **After an agent finishes, read this first.** Before trusting any agent summary,
                    open **Agent-output triage** and answer: which files changed, which commands ran,
                    what was proven, what was not verified. Confidence is a claim, not evidence.
                    """
                ),
                kind="info",
            ),
        ]
    )
    orientation
    return


@app.cell
def _(mo):
    section = mo.ui.dropdown(
        options=[
            "Course guide",
            "Glossary",
            "Workbook drills",
            "Answer key",
            "Quick reference",
            "Command anatomy",
            "Agent-output triage",
        ],
        value="Course guide",
        label="Section",
    )
    section
    return (section,)


@app.cell
def _(read_md, split_sections):
    course_sections = split_sections(read_md("course_guide.md"))
    return (course_sections,)


@app.cell
def _(extract_glossary_rows, read_md):
    glossary_rows = extract_glossary_rows(read_md("glossary.md"))
    return (glossary_rows,)


@app.cell
def _(extract_drills, read_md):
    drills = extract_drills(read_md("workbook.md"))
    return (drills,)


@app.cell
def _(extract_answers, read_md):
    answers = extract_answers(read_md("answer_key.md"))
    return (answers,)


@app.cell
def _(read_md):
    quick_reference_md = read_md("quick_reference.md")
    return (quick_reference_md,)


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


@app.cell
def _(course_sections, mo):
    _titles = [_t for _t, _ in course_sections]
    course_selector = mo.ui.dropdown(
        options=_titles,
        value=_titles[0] if _titles else None,
        label="Module",
    )
    return (course_selector,)


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
def _(drills, mo):
    _titles = [_t for _t, _ in drills]
    drill_selector = mo.ui.dropdown(
        options=_titles,
        value=_titles[0] if _titles else None,
        label="Drill",
    )
    show_answer = mo.ui.checkbox(label="Reveal answer", value=False)
    return drill_selector, show_answer


@app.cell
def _(answers, mo):
    _titles = [_t for _t, _ in answers]
    answer_selector = mo.ui.dropdown(
        options=_titles,
        value=_titles[0] if _titles else None,
        label="Answer",
    )
    return (answer_selector,)


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
    app_launched = mo.ui.checkbox(label="App launched / workflow exercised")
    live = mo.ui.checkbox(label="Live mode or live data claimed")
    dry_run = mo.ui.checkbox(label="Dry-run used")
    fixture = mo.ui.checkbox(label="Fixture or mock used")
    docs_only = mo.ui.checkbox(label="Docs-only")
    audit_only = mo.ui.checkbox(label="Audit-only")
    blocked = mo.ui.checkbox(label="Blocked")
    unsafe = mo.ui.checkbox(label="Unsafe or unclear")
    return (
        summary,
        files,
        commands,
        app_launched,
        live,
        dry_run,
        fixture,
        docs_only,
        audit_only,
        blocked,
        unsafe,
    )


@app.cell
def _(
    answer_selector,
    answers,
    app_launched,
    audit_only,
    blocked,
    classification_kind,
    classify_run,
    command_examples,
    command_selector,
    commands,
    course_sections,
    course_selector,
    docs_only,
    drill_selector,
    drills,
    dry_run,
    files,
    fixture,
    glossary_category,
    glossary_rows,
    glossary_search,
    live,
    mo,
    quick_reference_md,
    section,
    show_answer,
    summary,
    unsafe,
):
    _value = section.value

    if _value == "Course guide":
        _body = next(
            (_b for _t, _b in course_sections if _t == course_selector.value),
            course_sections[0][1] if course_sections else "",
        )
        main_panel = mo.vstack(
            [
                mo.md("## Course guide"),
                mo.md(
                    "Reading material, organized by module. Pick a module from the selector. "
                    "Use **Glossary** to look up unfamiliar terms."
                ),
                course_selector,
                mo.md(_body),
            ]
        )

    elif _value == "Glossary":
        _query = (glossary_search.value or "").lower().strip()
        _filtered = []
        for _row in glossary_rows:
            if glossary_category.value != "All" and _row["category"] != glossary_category.value:
                continue
            if _query and _query not in " ".join(_row.values()).lower():
                continue
            _filtered.append(_row)
        _table = mo.ui.table(
            data=[
                {
                    "Term": _r["term"],
                    "Category": _r["category"],
                    "Definition": _r["definition"],
                    "Why you see it": _r["why_seen"],
                    "What to ask": _r["ask"],
                }
                for _r in _filtered
            ],
            selection=None,
            pagination=True,
            page_size=25,
            wrapped_columns=["Definition", "Why you see it", "What to ask"],
        )
        main_panel = mo.vstack(
            [
                mo.md("## Glossary"),
                mo.md(
                    "Fast lookup for terms you see in agent output. "
                    "Filter by category or search across every column."
                ),
                mo.hstack(
                    [glossary_category, glossary_search],
                    justify="start",
                    widths=[0, 1],
                    gap=1.0,
                ),
                mo.md(f"**{len(_filtered)}** entries shown."),
                _table,
            ]
        )

    elif _value == "Workbook drills":
        _drill_body = next(
            (_b for _t, _b in drills if _t == drill_selector.value),
            "No drill found.",
        )
        _match_id = (
            drill_selector.value.split(" ", 1)[1]
            if drill_selector.value and " " in drill_selector.value
            else ""
        )
        _matching_answer = next(
            (
                _b
                for _t, _b in answers
                if _t.split(" ", 1)[1] == _match_id
            ),
            None,
        )
        _items = [
            mo.md("## Workbook drills"),
            mo.md(
                "Practice reading what agents produce. Pick a drill, answer in your head, "
                "then reveal the intended interpretation."
            ),
            mo.hstack([drill_selector, show_answer], justify="start", gap=1.0),
            mo.md(_drill_body),
        ]
        if show_answer.value and _matching_answer:
            _items.append(
                mo.callout(mo.md(_matching_answer), kind="success")
            )
        elif show_answer.value:
            _items.append(
                mo.callout(
                    mo.md(
                        "No matching answer found. Open **Answer key** and pick the answer "
                        "with the same number."
                    ),
                    kind="info",
                )
            )
        else:
            _items.append(
                mo.callout(
                    mo.md("Answer hidden. Toggle **Reveal answer** when ready."),
                    kind="neutral",
                )
            )
        main_panel = mo.vstack(_items)

    elif _value == "Answer key":
        _body = next(
            (_b for _t, _b in answers if _t == answer_selector.value),
            "No answer found.",
        )
        main_panel = mo.vstack(
            [
                mo.md("## Answer key"),
                mo.md(
                    "Intended supervisor interpretation for each workbook drill. "
                    "Use this after attempting the drill on your own."
                ),
                answer_selector,
                mo.md(_body),
            ]
        )

    elif _value == "Quick reference":
        main_panel = mo.vstack(
            [
                mo.md("## Quick reference"),
                mo.md(
                    "One-page cheat sheet for triaging an agent run. "
                    "Pair it with the **Agent-output triage** form."
                ),
                mo.md(quick_reference_md),
            ]
        )

    elif _value == "Command anatomy":
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
        main_panel = mo.vstack(
            [
                mo.md("## Command anatomy"),
                mo.md(
                    "Pick a real command. The breakdown explains program, subcommand, flags, "
                    "arguments, target, and what the command actually proves."
                ),
                command_selector,
                mo.md(f"```bash\n{command_selector.value}\n```"),
                mo.md("| Part | Meaning |\n|---|---|\n" + _rows),
            ]
        )

    elif _value == "Agent-output triage":
        _label, _reason, _notes, _prompt = classify_run(
            summary.value or "",
            files.value or "",
            commands.value or "",
            bool(app_launched.value),
            bool(live.value),
            bool(dry_run.value),
            bool(fixture.value),
            bool(docs_only.value),
            bool(audit_only.value),
            bool(blocked.value),
            bool(unsafe.value),
        )
        _notes_md = "\n".join(f"- {_n}" for _n in _notes)
        _kind = classification_kind(_label)
        main_panel = mo.vstack(
            [
                mo.md("## Agent-output triage"),
                mo.md(
                    "Use this after every agent run. Paste the agent's summary, list changed files, "
                    "paste the commands run, and toggle the flags that match the run."
                ),
                summary,
                files,
                commands,
                mo.md("**Run flags**"),
                mo.hstack(
                    [app_launched, live, dry_run, fixture],
                    justify="start",
                    gap=1.0,
                    wrap=True,
                ),
                mo.hstack(
                    [docs_only, audit_only, blocked, unsafe],
                    justify="start",
                    gap=1.0,
                    wrap=True,
                ),
                mo.callout(
                    mo.md(
                        f"### Classification: {_label}\n\n"
                        f"**Reason:** {_reason}\n\n"
                        f"**Data-source notes:**\n{_notes_md}\n\n"
                        f"**Suggested next prompt:**\n\n```text\n{_prompt}\n```"
                    ),
                    kind=_kind,
                ),
            ]
        )

    else:
        main_panel = mo.md("Pick a section above.")

    main_panel
    return


if __name__ == "__main__":
    app.run()
