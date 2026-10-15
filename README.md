# IAP App

## Concept Brief

The Student Task Manager is an application designed to help college students organize and manage their academic responsibilities in one place. The application will allow users to create, view, update, and delete academic tasks, track due dates, and manage workload across multiple courses.

## Repository Overview

This project is a student-focused academic planning prototype for managing coursework, degree progress, and planning decisions. It includes support for:

- Student profile setup and academic data entry
- Course catalog management and status tracking
- Degree requirements and audit progress
- Prerequisite relationships between courses
- Transcript updates and grade tracking
- Semester planning and generated academic plans
- Risk analysis for course planning challenges
- CSV import/export for catalog and student data

The application is intended as a planning supplement rather than an official degree audit or advising system. It should be reviewed against the student's published catalog and advisor guidance before use for formal academic decisions.

## Key Features

- Academic profile management for major, catalog year, standing, GPA, and graduation target
- Course catalog with search, update, and deletion workflows
- Requirement tracking by category and credit totals
- Prerequisite management and direct dependency checks
- “What-if” scenario analysis for adding, postponing, or dropping courses
- Semester planner with generated plan support
- Risk detection for prerequisite gaps and overloaded terms
- Data center utilities for CSV import/export and course records

## Tech Stack

- **Language:** Python
- **Framework:** Flask
- **Templating:** Jinja2
- **Persistence:** SQLite
- **Testing Framework:** pytest
- **Package Manager:** pip
- **Version Control:** Git
- **Repository:** GitHub
- **AI Coding Tool:** GitHub Copilot

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in a browser.

To run checks:

```bash
python -m py_compile app.py database.py tests/test_app.py
pytest -q
```

## Application Structure

```text
app.py
database.py
README.md
requirements.txt
requirements-dev.txt
static/
templates/
tests/
```

## Project Status

This package includes the core application logic, SQLite-backed workflow, and testing scaffolding for an academic planning prototype. The project is structured for future expansion and can be adapted to a larger, production-style academic planning system with stronger validation, role-based rules, and official catalog integration.

## Notes

- The seeded catalog data is example data only and should not be treated as authoritative institutional data.
- Degree checks are prototype-level logic and should be reviewed with a university advisor.
- The app is designed to support planning decisions, not replace formal academic advising or registrar records.

---

This repository content was expanded to include a more complete project overview and a clearer description of the application’s purpose, architecture, and operational workflow.
