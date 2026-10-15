# Tiger Engineering Pathway — Consolidated Project Guide

This is the one-file reading guide for the main course artifacts. The full versions remain in their modular files under `docs/`.

## 1. Project definition

Tiger Engineering Pathway is a course-planning application aimed at University of Memphis engineering students. It organizes academic profile information, course catalog entries, degree requirements, prerequisites, transcript status, and proposed semester plans to help students reason about a path toward graduation. It is a supplement to official degree-audit and advising processes—not a replacement for them.

## 2. M2 requirements and AI elicitation audit

The eight user stories are:

1. **Create Academic Profile** — record major, catalog year, standing, completed credits, and target term.
2. **View Remaining Degree Requirements** — show completed versus required credit/progress and missing requirements.
3. **Identify Course Prerequisites** — see required courses and flag unmet prerequisites.
4. **Prioritize Courses** — order candidate courses based on prerequisites, core/capstone relevance, status, planning, and offering availability, with reasons.
5. **Create Semester Course Plan** — assign courses to future terms and review credits by term.
6. **Project Graduation Date** — calculate an estimated graduation term from remaining requirements, prerequisites, offerings, and term load; distinguish that estimate from a manually entered target.
7. **Perform What-If Analysis** — assess changes such as adding, removing, or postponing a course without silently changing the saved plan.
8. **Identify Graduation Risks** — flag prerequisite risks, overloaded terms, or potentially unfinishable requirements.

### Falsifiable NFRs

- **NFR-01:** Priority recommendations return within 3 seconds for at least 95% of requests under normal operating load.
- **NFR-02:** Projected graduation term is recalculated and displayed within 5 seconds after a plan change is accepted.
- **NFR-03:** Across 100 test cases containing incomplete prerequisite relationships, zero recommended courses violate required prerequisites.

### AI elicitation audit summary

AI helped organize candidate stories, acceptance criteria, and measurable quality thresholds. Human review kept the app focused on engineering academic planning, retained eight stories, emphasized testable acceptance criteria, and marked future capabilities as incomplete rather than pretending they already work. Catalog correctness is a human data-quality responsibility. The maintained audit is a consolidated repository record, not a verbatim transcript of an unavailable original AI chat.

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

A student creates a course plan; the plan contains one or more semesters; each semester can contain zero or more planned courses; each planned placement references a catalog course; requirements can include courses through a many-to-many relation; and course prerequisites link course objects recursively.

### AI critique

The model is requirement-driven and avoids over-modeling generic roles/settings or turning computed priority/risk/projection outputs into entities unnecessarily. The key critique is that v3's SQLite prototype stores `planned_term` and status on shared course rows and has a single fixed student row. That does not yet fully implement separate `CoursePlan`, `Semester`, and `PlannedCourse` entities, which would be necessary for multiple saved plans or isolated what-if scenarios. Prerequisite cycles, accurate requirement mappings, catalog provenance, and separating target graduation from computed projection also need more work.

See [Domain Model](domain-model/domain-model.md) and [AI Critique](domain-model/ai-critique.md).

## 4. ADR-001 — Course Data Architecture

**Decision:** Use structured course data and separate student course selections.

**Alternatives:**

- Hard-code courses and requirements in application code: initially simple, but changes and support for new majors require code changes.
- Use unrestricted free-text course input: flexible for users, but course identity, credits, prerequisites, and requirement checks become inconsistent.
- Selected: structured course information plus separate student planning choices.

**Tradeoffs:** Consistency, extensibility, prerequisite processing, and clearer student histories improve. Modeling, validation, maintenance, and dependency on accurate catalog data become harder. The project does not replace official advising/degree audit.

Full version: [ADR-001](adr/ADR-001-course-data-architecture.md); its [prompt-and-diff log](adr/prompt-and-diff-log.md) preserves the initial prompt, AI-assisted framing, human review, and final changes.

## 5. Walking skeleton

The selected thin slice is Student Profile creation/update:

1. Browser loads Student Setup.
2. User submits the profile form.
3. Flask route receives the request.
4. `database.py` writes the profile to SQLite.
5. The route redirects; the next request calls `database.py` to query the saved row.
6. The page displays the stored profile.
7. Pytest checks the HTTP path and database value.

The GitHub Actions workflow compiles Python files and runs tests on pushes and pull requests. The source assignment also requires a green run URL and runtime screenshot/recording; those must be captured after publishing and executing CI on GitHub.

Full version: [Walking Skeleton and CI](walking-skeleton/walking-skeleton.md).

## 6. v3 code and its boundaries

The application includes a Flask/Jinja dashboard, student setup, course catalog, requirements, transcript, prerequisites, degree audit, priority, what-if screen, planner/auto-plan, risk analysis, data center, CSV import/export, and SQLite persistence. The Student Setup path uses `database.py`; several other screens still access SQLite directly from `app.py`.

Known limitations are recorded in the main README: sample course data is not authoritative; requirement mapping fallback is simplified; graduation target is stored rather than fully calculated; what-if simulation is rudimentary; and priority/planner/risk algorithms are prototypes. Do not claim those unfinished behaviors or performance NFRs as complete.

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

## 8. AI-use disclosure

AI support was used for drafting and organization. Human review owned project scope, the course-data decision, entity selection, and final acceptance criteria. AI-generated content is not evidence that a feature is implemented, a test has passed, a requirement is official, or a CI run is green.

More detail: [AI-use disclosure](ai-use/ai-use-disclosure.md).
