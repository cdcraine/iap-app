# Tiger Engineering Pathway — Consolidated Project Guide

This is the one-file reading guide for the main course artifacts. The full versions remain in their modular files under `docs/`.

## 1. Project definition

Tiger Engineering Pathway is a course-planning application aimed at University of Memphis engineering students. It organizes academic profile information, course catalog entries, degree requirement[...]

## 2. M2 requirements and AI elicitation audit

The eight user stories are:

1. **Create Academic Profile** — record major, catalog year, standing, completed credits, and target term.
2. **View Remaining Degree Requirements** — show completed versus required credit/progress and missing requirements.
3. **Identify Course Prerequisites** — see required courses and flag unmet prerequisites.
4. **Prioritize Courses** — order candidate courses based on prerequisites, core/capstone relevance, status, planning, and offering availability, with reasons.
5. **Create Semester Course Plan** — assign courses to future terms and review credits by term.
6. **Project Graduation Date** — calculate an estimated graduation term from remaining requirements, prerequisites, offerings, and term load; distinguish that estimate from a manually entered ta[...]
7. **Perform What-If Analysis** — assess changes such as adding, removing, or postponing a course without silently changing the saved plan.
8. **Identify Graduation Risks** — flag prerequisite risks, overloaded terms, or potentially unfinishable requirements.

### Falsifiable NFRs

- **NFR-01:** Priority recommendations return within 3 seconds for at least 95% of requests under normal operating load.
- **NFR-02:** Projected graduation term is recalculated and displayed within 5 seconds after a plan change is accepted.
- **NFR-03:** Across 100 test cases containing incomplete prerequisite relationships, zero recommended courses violate required prerequisites.

### AI elicitation audit summary

AI helped organize candidate stories, acceptance criteria, and measurable quality thresholds. Human review kept the app focused on engineering academic planning, retained eight stories, emphasized[...]

Full version: [Requirements and AI Elicitation Audit](requirements/requirements-and-ai-elicitation-audit.md).

## 3. Domain model

### Core concepts

- **Student:** student ID, name, major, catalog year, target graduation semester.
- **Course:** course code, name, credits, description.
- **DegreeRequirement:** requirement ID, name, type, required credits.
- **CoursePlan:** plan ID, created date, name.
- **Semester:** semester ID, term, year.
- **PlannedCourse:** planned-course ID, status, notes.
- **Course prerequisite relationship:** a course-to-course relationship, not a separate core entity.

### Relationships

A student creates a course plan; the plan contains one or more semesters; each semester can contain zero or more planned courses; each planned placement references a catalog course; requirements c[...]

### AI critique

The model is requirement-driven and avoids over-modeling generic roles/settings or turning computed priority/risk/projection outputs into entities unnecessarily. The key critique is that v3's SQLi[...]

See [Domain Model](domain-model/domain-model.md) and [AI Critique](domain-model/ai-critique.md).

## 4. ADR-001 — Course Data Architecture

**Decision:** Use structured course data and separate student course selections.

**Alternatives:**

- Hard-code courses and requirements in application code: initially simple, but changes and support for new majors require code changes.
- Use unrestricted free-text course input: flexible for users, but course identity, credits, prerequisites, and requirement checks become inconsistent.
- Selected: structured course information plus separate student planning choices.

**Tradeoffs:** Consistency, extensibility, prerequisite processing, and clearer student histories improve. Modeling, validation, maintenance, and dependency on accurate catalog data become harder.[...]

Full version: [ADR-001](adr/ADR-001-course-data-architecture.md); its [prompt-and-diff log](adr/prompt-and-diff-log.md) preserves the initial prompt, AI-assisted framing, human review, and final c[...]

## 5. Walking skeleton

The selected thin slice is Student Profile creation/update:

1. Browser loads Student Setup.
2. User submits the profile form.
3. Flask route receives the request.
4. `database.py` writes the profile to SQLite.
5. The route redirects; the next request calls `database.py` to query the saved row.
6. The page displays the stored profile.
7. Pytest checks the HTTP path and database value.

The GitHub Actions workflow compiles Python files and runs tests on pushes and pull requests. The source assignment also requires a green run URL and runtime screenshot/recording; those must be ca[...]

Full version: [Walking Skeleton and CI](walking-skeleton/walking-skeleton.md).

## 6. v3 code and its boundaries

The application includes a Flask/Jinja dashboard, student setup, course catalog, requirements, transcript, prerequisites, degree audit, priority, what-if screen, planner/auto-plan, risk analysis, [...]

Known limitations are recorded in the main README: sample course data is not authoritative; requirement mapping fallback is simplified; graduation target is stored rather than fully calculated; wh[...]

## 7. Running and verifying

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m py_compile app.py database.py tests/test_app.py
pytest -q
python app.py
```

Then open <http://127.0.0.1:5000>.

## 8. M5 Testing Assignment

Objective

The M5 Testing Assignment verifies core application behavior and demonstrates a working test suite and CI integration for this project. The assignment focuses on unit and integration tests for the walking-skeleton features and key logic (profile persistence, degree requirement checks, prerequisite enforcement, and basic planner behaviors).

Tasks

- Write pytest-based unit tests and Flask test-client integration tests under `tests/`.
  - Test Student Profile create/read/update via the Flask routes and `database.py` (use a test database or temporary SQLite file).
  - Add tests for degree-requirement calculations and remaining-credits logic.
  - Add tests that exercise prerequisite-checking logic and ensure no recommended course violates prerequisites (to support NFR-03).
  - Add at least one integration test for creating a semester plan and verifying the projected graduation term recalculation.
- Add fixtures for test data (sample courses, requirements, and student profiles) in `tests/conftest.py`.
- Aim for a minimum test coverage threshold (suggested: 80%) and add a coverage run in CI if not already present.
- Ensure tests run in GitHub Actions and that the workflow reports a green pass for the tests.

Acceptance criteria

- Tests are added to `tests/` and run locally with `pytest -q`.
- CI (GitHub Actions) passes on the branch/PR containing the tests.
- Test coverage meets or exceeds the project's target (document the threshold in the PR).
- A specific test (or test set) demonstrates NFR-03 by validating, across a representative set of cases, that recommended courses do not violate required prerequisites.
- Deliverables: Pull request with tests, CI green run URL, and a short runtime screenshot/recording showing the tests executing.

How to run the tests

```bash
# from the project root
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest -q
```

Notes and tips

- Use temporary filesystem fixtures or `sqlite:///:memory:` for isolated database tests.
- Keep tests deterministic: seed sample data and avoid relying on external services.
- For performance-related NFRs (NFR-01/NFR-02), add targeted tests that measure execution time and assert they complete within the expected window; if those tests are flaky in CI, document mitigation steps and thresholds.

Full version: See the course assignment sheet or add a detailed testing plan in `docs/testing/m5-testing-assignment.md`.

## 9. AI-use disclosure

AI support was used for drafting and organization. Human review owned project scope, the course-data decision, entity selection, and final acceptance criteria. AI-generated content is not evidenc[...]

More detail: [AI-use disclosure](ai-use/ai-use-disclosure.md).
