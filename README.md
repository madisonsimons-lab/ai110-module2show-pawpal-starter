# PawPal+

PawPal+ is a Streamlit pet-care planner that helps an owner organize daily tasks for one or more pets.
It combines task management with scheduling logic so owners can quickly see what to do, when to do it, and whether their plan has conflicts.

## Features

- Owner and pet management with validation of ownership relationships.
- Task scheduling with due date, due time, frequency, priority, and duration.
- Chronological sorting algorithms:
	- Sort by time.
	- Sort by priority then time.
	- Sort by date then time.
- Daily plan generation (`getTodaysTasks`) sorted by priority and time.
- Advanced filtering:
	- By pet.
	- By completion status.
	- By time window.
	- Combined filter by status and pet.
- Recurrence logic:
	- Marking daily/weekly tasks complete can create the next occurrence automatically.
	- Recurring schedule expansion across a date range.
- Advanced algorithmic capability:
	- `find_next_available_slot` scans a configurable time window and returns the earliest conflict-free slot for a pet.
- Conflict intelligence:
	- Detect overlapping task-duration conflicts.
	- Detect same-time warning conflicts.
	- Human-readable warning and conflict reports.
- Data persistence:
	- Owner, pets, and tasks are serialized to `data.json`.
	- Streamlit loads persisted data on startup and auto-saves when pets/tasks are added.
- Streamlit UI enhancements:
	- Clear schedule table output.
	- Visual feedback with `st.success`, `st.warning`, and `st.info`.
	- Priority color coding (`🔴 High`, `🟡 Medium`, `🔵 Low`) and task-type emojis in the schedule table.
	- Conflict warnings displayed directly in the planning workflow.

## System Design

Core classes:

- `Owner`: manages pets and aggregates tasks across pets.
- `Pet`: stores profile information and task list.
- `Task`: stores scheduling fields and recurrence metadata.
- `Scheduler`: orchestrates sorting, filtering, recurrence handling, and conflict detection.

Final UML artifacts:

- Mermaid source: `uml_final.mmd`
- Diagram image: `uml_final.png`

## Project Structure

```text
.
├── app.py
├── main.py
├── pawpal_system.py
├── tests/
│   └── test_pawpal.py
├── uml_final.mmd
├── uml_final.png
└── README.md
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run The App

```bash
streamlit run app.py
```

## Agent Mode Usage

Agent Mode was used to plan and execute the advanced scheduler upgrades in discrete phases:

1. Planned JSON persistence for nested objects and selected custom dictionary conversion over marshmallow to avoid external dependencies.
2. Implemented `Owner.save_to_json` and `Owner.load_from_json` in `pawpal_system.py` and wired startup loading/auto-save behavior in `app.py`.
3. Added an advanced scheduling algorithm (`find_next_available_slot`) and integrated it into Streamlit as an interactive suggestion tool.
4. Refined priority-first scheduling and UI formatting with emoji-based priority/status indicators for higher readability.

This workflow made it easier to keep architecture decisions consistent while still shipping features quickly.

## Run Tests

```bash
python3 -m pytest -q
```

Current automated test suite coverage includes:

- Sorting correctness (chronological ordering).
- Recurrence logic for daily and weekly follow-up tasks.
- Conflict detection for overlaps and duplicate times.
- Filtering behavior by pet, status, and time window.

## 📸 Demo

<a href="/course_images/ai110/pawpal_streamlit_demo.png" target="_blank"><img src='/course_images/ai110/pawpal_streamlit_demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Reliability

Confidence level from current test results: 4/5 stars.