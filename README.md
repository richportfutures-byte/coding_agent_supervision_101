# Coding Agent Supervision 101

A reference-first Marimo notebook app for **Coding Agent Supervision for Non-Developers**.

This project teaches non-developers how to supervise coding-agent work in real repositories by reading commands, files, Git output, diffs, tests, runtime claims, safety boundaries, and agent summaries.

## Project layout

```text
coding_agent_supervision_101/
  course_app.py
  content/
    course_guide.md
    glossary.md
    workbook.md
    answer_key.md
    quick_reference.md
  assets/
  pyproject.toml
  README.md
```

## Run locally

From the repo root:

```bash
uv sync
uv run marimo edit course_app.py
```

Alternative, if Marimo is already installed:

```bash
marimo edit course_app.py
```

To run as an app:

```bash
uv run marimo run course_app.py
```

## What v1 includes

- Section selector for the course guide, workbook, glossary, answer key, and quick reference.
- Rendered Markdown content loaded from `content/` files.
- Glossary search and category filter.
- Workbook drill selector with answer reveal.
- Command anatomy examples with an interactive breakdown.
- Agent-output triage checklist form that classifies a coding-agent run.
- No scoring or progress engine yet.

## Design principle

This is reference-first, not quiz-engine-first. The learner should be able to keep the notebook open while supervising Codex, Claude Code, Gemini CLI, Windsurf, or another coding agent and use it to classify what happened after each agent run.
