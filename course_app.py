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
        path = CONTENT_DIR / filename
        if not path.exists():
            return f"# Missing content file\n\nExpected `{path}`."
        return path.read_text(encoding="utf-8")

    def split_sections(markdown_text: str, min_level: int = 1, max_level: int = 2):
        lines = markdown_text.splitlines()
        sections = []
        title = "Overview"
        current = []
        heading_re = re.compile(rf"^(#{{{min_level},{max_level}}})\s+(.+?)\s*$")
        for line in lines:
            match = heading_re.match(line)
            if match and current:
                sections.append((title, "\n".join(current).strip()))
                current = [line]
                title = match.group(2).strip()
            else:
                if match:
                    title = match.group(2).strip()
                current.append(line)
        if current:
            sections.append((title, "\n".join(current).strip()))
        return sections

    def extract_glossary_rows(markdown_text: str):
        rows = []
        category = "Uncategorized"
        for raw in markdown_text.splitlines():
            line = raw.strip()
            if line.startswith("## "):
                category = line[3:].strip()
                continue
            if not line.startswith("|") or "---" in line or "Term" in line:
                continue
            cells = [cell.strip().replace("**", "") for cell in line.strip("|").split("|")]
            if len(cells) >= 4:
                rows.append({
                    "category": category,
                    "term": cells[0],
                    "definition": cells[1],
                    "why_seen": cells[2],
                    "ask": cells[3],
                })
        return rows

    def extract_drills(markdown_text: str):
        body = markdown_text.split("# Section 6: Answer Key", 1)[0]
        matches = list(re.finditer(r"^## Drill\s+([^\n]+)\n", body, re.MULTILINE))
        drills = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            drills.append((f"Drill {match.group(1).strip()}", body[start:end].strip()))
        return drills

    def extract_answers(markdown_text: str):
        matches = list(re.finditer(r"^### Answer\s+([^\n]+)\n", markdown_text, re.MULTILINE))
        answers = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
            answers.append((f"Answer {match.group(1).strip()}", markdown_text[start:end].strip()))
        return answers

    def classify_run(summary, files, commands, app_launched, live, dry_run, fixture, docs_only, audit_only, blocked, unsafe):
        changed = [line.strip() for line in files.splitlines() if line.strip()]
        text = "\n".join([summary, files, commands]).lower()
        has_source = any(p.startswith(("src/", "app/", "scripts/")) or p in {"package.json", "pyproject.toml"} for p in changed)
        has_tests = "test" in text or any("test" in p for p in changed)
        has_pass = any(token in text for token in ("passed", "success", "built", "ok"))
        if unsafe:
            label = "Unsafe or unclear"
            reason = "Safety or evidence is unclear. Do not trust the run until boundaries are explicit."
            prompt = "Separate facts, interpretations, and unverified claims. Confirm whether secrets, live actions, destructive commands, or fallback paths were involved."
        elif blocked:
            label = "Blocked"
            reason = "The agent reports it could not or should not proceed. Blocked can be correct when safety or credentials prevent verification."
            prompt = "Name the exact blocker, what was completed before the blocker, and the smallest concrete implementation step after the blocker is removed."
        elif audit_only:
            label = "Audit-only"
            reason = "The work appears to inspect or recommend without changing behavior."
            prompt = "This is audit-only. Implement the smallest concrete behavior change now unless blocked."
        elif docs_only or (changed and all(p.endswith(".md") or p.startswith("docs/") for p in changed)):
            label = "Docs-only"
            reason = "Only documentation-style files are listed, so runtime behavior is not proven changed."
            prompt = "Do not call this implemented. Identify the source/config/script file that would have to change to affect runtime behavior."
        elif has_source and has_tests and (app_launched or live or dry_run or has_pass):
            label = "Implemented and verified" if app_launched or live else "Implemented but not runtime-verified"
            reason = "Source/config/script changes and verification evidence are present. Runtime/live proof depends on the selected verification source."
            prompt = "List exact changed runtime files, exact verification commands, what each command proved, and what was not verified."
        elif has_source:
            label = "Implemented but not verified"
            reason = "Source/config/script changes are present, but verification evidence is incomplete."
            prompt = "Run the focused tests or smallest runtime smoke for the changed operator path and report exact output."
        elif has_tests:
            label = "Test-only"
            reason = "Tests changed or ran, but no implementation file is visible."
            prompt = "What source change makes this test pass, and did the test fail before implementation?"
        else:
            label = "Needs follow-up"
            reason = "There is not enough structured evidence to classify the run."
            prompt = "List changed files, exact commands, test results, what now works, what was not verified, blockers, and Git state."
        notes = []
        if live:
            notes.append("Live selected: verify explicit opt-in, redacted secrets, read-only scope where relevant, and no fixture fallback.")
        if dry_run:
            notes.append("Dry run selected: do not treat this as live proof.")
        if fixture:
            notes.append("Fixture/mock selected: useful proof, not live proof.")
        if not notes:
            notes.append("Data source unknown: ask whether proof was live, mock, fixture, dry-run, static, or unknown.")
        return label, reason, notes, prompt

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
    titles = [title for title, _body in course_sections]
    course_selector = mo.ui.dropdown(options=titles, value=titles[0] if titles else None, label="Course section")
    if section.value == "Course guide":
        course_selector
    return course_sections, course_selector


@app.cell
def _(course_sections, course_selector, mo, section):
    if section.value == "Course guide":
        active = next((body for title, body in course_sections if title == course_selector.value), course_sections[0][1] if course_sections else "")
        mo.md(active)
    return


@app.cell
def _(extract_glossary_rows, mo, read_md, section):
    glossary_rows = extract_glossary_rows(read_md("glossary.md"))
    categories = ["All"] + sorted({row["category"] for row in glossary_rows})
    glossary_category = mo.ui.dropdown(options=categories, value="All", label="Glossary category")
    glossary_search = mo.ui.text(label="Search glossary")
    if section.value == "Glossary":
        mo.vstack([glossary_category, glossary_search])
    return glossary_category, glossary_rows, glossary_search


@app.cell
def _(glossary_category, glossary_rows, glossary_search, mo, section):
    if section.value == "Glossary":
        query = (glossary_search.value or "").lower()
        cards = []
        for row in glossary_rows:
            haystack = " ".join(row.values()).lower()
            if glossary_category.value != "All" and row["category"] != glossary_category.value:
                continue
            if query and query not in haystack:
                continue
            cards.append(mo.md(f"""### {row['term']}

**Category:** {row['category']}

**Definition:** {row['definition']}

**Why you see it:** {row['why_seen']}

**What to ask:** {row['ask']}
"""))
        mo.vstack([mo.md(f"Showing **{len(cards)}** entries."), *cards[:75]])
    return


@app.cell
def _(extract_drills, mo, read_md, section):
    drills = extract_drills(read_md("workbook.md"))
    drill_titles = [title for title, _ in drills]
    drill_selector = mo.ui.dropdown(options=drill_titles, value=drill_titles[0] if drill_titles else None, label="Workbook drill")
    show_answer = mo.ui.checkbox(label="Show answer pointer", value=False)
    if section.value == "Workbook drills":
        mo.vstack([drill_selector, show_answer])
    return drill_selector, drills, show_answer


@app.cell
def _(drill_selector, drills, mo, section, show_answer):
    if section.value == "Workbook drills":
        body = next((body for title, body in drills if title == drill_selector.value), "No drill found.")
        if show_answer.value:
            mo.vstack([mo.md(body), mo.callout("Use the Answer key section and select the matching answer for the full explanation.", kind="info")])
        else:
            mo.vstack([mo.md(body), mo.callout("Answer hidden. Toggle when ready.", kind="neutral")])
    return


@app.cell
def _(extract_answers, mo, read_md, section):
    answers = extract_answers(read_md("answer_key.md"))
    answer_titles = [title for title, _ in answers]
    answer_selector = mo.ui.dropdown(options=answer_titles, value=answer_titles[0] if answer_titles else None, label="Answer")
    if section.value == "Answer key":
        answer_selector
    return answer_selector, answers


@app.cell
def _(answer_selector, answers, mo, section):
    if section.value == "Answer key":
        body = next((body for title, body in answers if title == answer_selector.value), "No answer found.")
        mo.md(body)
    return


@app.cell
def _(mo, read_md, section):
    if section.value == "Quick reference":
        mo.md(read_md("quick_reference.md"))
    return


@app.cell
def _(mo, section):
    examples = {
        "uv run pytest -q tests/test_runtime_gate.py": "Program: uv. Nested program: pytest. Flag: -q. Target: tests/test_runtime_gate.py. Proves: focused tests passed. Does not prove: app launch, UI, or live data.",
        "git status --short": "Program: git. Subcommand: status. Flag: --short. Target: current repo working tree. Proves: changed/staged/untracked file state. Does not prove: app works.",
        "curl -s -o /dev/null -w '%{http_code}\\n' http://localhost:8000/api/health": "Program: curl. Target: local health endpoint. Proves: endpoint returns an HTTP status. Does not prove: full workflow works.",
        "SCHWAB_API_KEY=*** uv run python scripts/run_live_smoke.py --opt-in-live --symbol SPY --max-calls 1 --read-only": "Redacted env var plus bounded live smoke. Verify explicit opt-in, read-only scope, no secrets printed, and no fixture fallback.",
    }
    command_selector = mo.ui.dropdown(options=list(examples), value=list(examples)[0], label="Command example")
    if section.value == "Command anatomy":
        command_selector
    return command_selector, examples


@app.cell
def _(command_selector, examples, mo, section):
    if section.value == "Command anatomy":
        mo.md(f"""## Command anatomy

```bash
{command_selector.value}
```

{examples[command_selector.value]}
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
        mo.vstack([summary, files, commands, mo.hstack([app_launched, live, dry_run, fixture]), mo.hstack([docs_only, audit_only, blocked, unsafe])])
    return app_launched, audit_only, blocked, commands, docs_only, dry_run, files, fixture, live, summary, unsafe


@app.cell
def _(app_launched, audit_only, blocked, classify_run, commands, docs_only, dry_run, files, fixture, live, mo, section, summary, unsafe):
    if section.value == "Agent-output triage checklist":
        label, reason, notes, prompt = classify_run(summary.value or "", files.value or "", commands.value or "", bool(app_launched.value), bool(live.value), bool(dry_run.value), bool(fixture.value), bool(docs_only.value), bool(audit_only.value), bool(blocked.value), bool(unsafe.value))
        mo.md(f"""## Classification

**{label}**

**Reason:** {reason}

**Data-source notes:**
{chr(10).join('- ' + note for note in notes)}

**Next prompt:**

```text
{prompt}
```
""")
    return


if __name__ == "__main__":
    app.run()
