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

    return mo, read_md, split_sections, extract_glossary_rows, extract_drills, extract_answers, classify_run


@app.cell
def _(mo):
    mo.md("""
    # Coding Agent Supervision 101

    Reference-first Marimo notebook app for non-developers supervising coding agents in real repositories.
    """)
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
            "Agent-output triage checklist",
        ],
        value="Course guide",
        label="Section",
    )
    section
    return section,


@app.cell
def _(mo, read_md, section, split_sections):
    course_sections = split_sections(read_md("course_guide.md"))
    course_titles = [_section_title for _section_title, _section_body in course_sections]
    course_selector = mo.ui.dropdown(
        options=course_titles,
        value=course_titles[0] if course_titles else None,
        label="Course section",
    )
    if section.value == "Course guide":
        course_selector
    return course_sections, course_selector


@app.cell
def _(course_sections, course_selector, mo, section):
    if section.value == "Course guide":
        _active_course_body = next(
            (_section_body for _section_title, _section_body in course_sections if _section_title == course_selector.value),
            course_sections[0][1] if course_sections else "",
        )
        mo.md(_active_course_body)
    return


@app.cell
def _(extract_glossary_rows, mo, read_md, section):
    glossary_rows = extract_glossary_rows(read_md("glossary.md"))
    glossary_categories = ["All"] + sorted({_row["category"] for _row in glossary_rows})
    glossary_category = mo.ui.dropdown(options=glossary_categories, value="All", label="Glossary category")
    glossary_search = mo.ui.text(label="Search glossary")
    if section.value == "Glossary":
        mo.vstack([glossary_category, glossary_search])
    return glossary_category, glossary_rows, glossary_search


@app.cell
def _(glossary_category, glossary_rows, glossary_search, mo, section):
    if section.value == "Glossary":
        _query = (glossary_search.value or "").lower()
        _cards = []
        for _row in glossary_rows:
            _haystack = " ".join(_row.values()).lower()
            if glossary_category.value != "All" and _row["category"] != glossary_category.value:
                continue
            if _query and _query not in _haystack:
                continue
            _cards.append(mo.md(f"""### {_row['term']}

**Category:** {_row['category']}

**Definition:** {_row['definition']}

**Why you see it:** {_row['why_seen']}

**What to ask:** {_row['ask']}
"""))
        mo.vstack([mo.md(f"Showing **{len(_cards)}** entries."), *_cards[:75]])
    return


@app.cell
def _(extract_drills, mo, read_md, section):
    drills = extract_drills(read_md("workbook.md"))
    drill_titles = [_drill_title for _drill_title, _drill_body in drills]
    drill_selector = mo.ui.dropdown(
        options=drill_titles,
        value=drill_titles[0] if drill_titles else None,
        label="Workbook drill",
    )
    show_answer = mo.ui.checkbox(label="Show answer pointer", value=False)
    if section.value == "Workbook drills":
        mo.vstack([drill_selector, show_answer])
    return drill_selector, drills, show_answer


@app.cell
def _(drill_selector, drills, mo, section, show_answer):
    if section.value == "Workbook drills":
        _active_drill_body = next(
            (_drill_body for _drill_title, _drill_body in drills if _drill_title == drill_selector.value),
            "No drill found.",
        )
        if show_answer.value:
            mo.vstack([
                mo.md(_active_drill_body),
                mo.callout("Use the Answer key section and select the matching answer for the full explanation.", kind="info"),
            ])
        else:
            mo.vstack([
                mo.md(_active_drill_body),
                mo.callout("Answer hidden. Toggle when ready.", kind="info"),
            ])
    return


@app.cell
def _(extract_answers, mo, read_md, section):
    answers = extract_answers(read_md("answer_key.md"))
    answer_titles = [_answer_title for _answer_title, _answer_body in answers]
    answer_selector = mo.ui.dropdown(
        options=answer_titles,
        value=answer_titles[0] if answer_titles else None,
        label="Answer",
    )
    if section.value == "Answer key":
        answer_selector
    return answer_selector, answers


@app.cell
def _(answer_selector, answers, mo, section):
    if section.value == "Answer key":
        _active_answer_body = next(
            (_answer_body for _answer_title, _answer_body in answers if _answer_title == answer_selector.value),
            "No answer found.",
        )
        mo.md(_active_answer_body)
    return


@app.cell
def _(mo, read_md, section):
    if section.value == "Quick reference":
        mo.md(read_md("quick_reference.md"))
    return


@app.cell
def _(mo, section):
    command_examples = {
        "uv run pytest -q tests/test_runtime_gate.py": "Program: uv. Nested program: pytest. Flag: -q. Target: tests/test_runtime_gate.py. Proves: focused tests passed. Does not prove: app launch, UI, or live data.",
        "git status --short": "Program: git. Subcommand: status. Flag: --short. Target: current repo working tree. Proves: changed/staged/untracked file state. Does not prove: app works.",
        "curl -s -o /dev/null -w '%{http_code}\\n' http://localhost:8000/api/health": "Program: curl. Target: local health endpoint. Proves: endpoint returns an HTTP status. Does not prove: full workflow works.",
        "SCHWAB_API_KEY=*** uv run python scripts/run_live_smoke.py --opt-in-live --symbol SPY --max-calls 1 --read-only": "Redacted env var plus bounded live smoke. Verify explicit opt-in, read-only scope, no secrets printed, and no fixture fallback.",
    }
    command_selector = mo.ui.dropdown(
        options=list(command_examples),
        value=list(command_examples)[0],
        label="Command example",
    )
    if section.value == "Command anatomy":
        command_selector
    return command_examples, command_selector


@app.cell
def _(command_examples, command_selector, mo, section):
    if section.value == "Command anatomy":
        mo.md(f"""## Command anatomy

```bash
{command_selector.value}
```

{command_examples[command_selector.value]}
""")
    return


@app.cell
def _(mo, section):
    summary = mo.ui.text_area(label="Paste agent summary", rows=7)
    files = mo.ui.text_area(label="Changed files, one per line", rows=5)
    commands = mo.ui.text_area(label="Commands/tests run", rows=5)
    app_launched = mo.ui.checkbox(label="App launched / workflow exercised")
    live = mo.ui.checkbox(label="Live mode or live data claimed")
    dry_run = mo.ui.checkbox(label="Dry-run used")
    fixture = mo.ui.checkbox(label="Fixture or mock used")
    docs_only = mo.ui.checkbox(label="Docs-only")
    audit_only = mo.ui.checkbox(label="Audit-only")
    blocked = mo.ui.checkbox(label="Blocked")
    unsafe = mo.ui.checkbox(label="Unsafe or unclear")
    if section.value == "Agent-output triage checklist":
        mo.vstack([
            summary,
            files,
            commands,
            mo.hstack([app_launched, live, dry_run, fixture]),
            mo.hstack([docs_only, audit_only, blocked, unsafe]),
        ])
    return app_launched, audit_only, blocked, commands, docs_only, dry_run, files, fixture, live, summary, unsafe


@app.cell
def _(app_launched, audit_only, blocked, classify_run, commands, docs_only, dry_run, files, fixture, live, mo, section, summary, unsafe):
    if section.value == "Agent-output triage checklist":
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
        _notes_markdown = chr(10).join(f"- {_note}" for _note in _notes)
        mo.md(f"""## Classification

**{_label}**

**Reason:** {_reason}

**Data-source notes:**
{_notes_markdown}

**Next prompt:**

```text
{_prompt}
```
""")
    return


if __name__ == "__main__":
    app.run()
