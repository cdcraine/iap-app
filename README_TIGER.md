# Tiger Engineering Pathway

**University of Memphis-inspired engineering academic planning prototype**

Tiger Engineering Pathway is intended to help engineering students organize academic profile information, courses, requirements, prerequisites, transcript status, and semester plans. It is a planning supplement—not an official degree audit, registrar record, or replacement for academic advising. All degree requirements and course data must be checked against the student's applicable catalog and an advisor.

> **Repository status:** This package consolidates the Tiger Engineering Pathway v3 application and project artifacts for GitHub. The code includes a local SQLite database, Flask/Jinja interface, automated smoke/persistence tests, and a GitHub Actions workflow. A green GitHub Actions run URL and fresh browser recording are not included because the workflow has not yet been run from the user's GitHub repository.

## Quick start (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m py_compile app.py database.py tests/test_app.py
pytest -q
```

Open <http://127.0.0.1:5000>.

To run checks:

```bash
python -m py_compile app.py tests/test_app.py
pytest -q
```

The demo database is created as `tiger_pathway.db` in the project directory by default. It is ignored by Git. Tests use a temporary database. A sample student record is seeded for demonstration and is not official student data.

## Main screens

| Screen | Route | Purpose in the v3 prototype |
|---|---|---|
| Dashboard | `/` | Snapshot of course status, credits, and detected risks |
| Student Setup | `/student` | Update the academic profile; writes to SQLite and redirects to read the saved record |
| Course Catalog | `/catalog` | Add, search, and update course entries |
| Degree Requirements | `/requirements` | Review and maintain requirement categories |
| Transcript Entry | `/transcript` | Update course completion statuses and grades |
| Prerequisites | `/prerequisites` | Maintain course prerequisite relationships |
| Degree Audit | `/audit` | Show progress against requirement categories |
| Course Priority | `/priority` | Show a rule-based priority score and explanation |
| What-If Analysis | `/what-if` | Prototype impact view for a selected course/action |
| Semester Planner | `/planner` | Assign courses to terms; `/auto-plan` provides a draft plan |
| Risk Analysis | `/risks` | Surface prerequisite and credit-load risk conditions |
| Data Center | `/data-center` | Course counts, CSV import, and exports |

This list describes available screens, not a claim that every graduation-planning feature is fully verified. See [known limitations](#known-limitations).

## Architecture at a glance

- **Presentation:** HTML templates under `templates/` and stylesheet `static/css/style.css`.
- **Application:** Flask routes in `app.py` validate/coordinate web requests and call SQLite.
- **Persistence:** SQLite tables for student profile, course catalog, requirements, course-requirement links, prerequisites, and what-if records.
- **Verification:** pytest tests and `.github/workflows/ci.yml` run on pushes and pull requests.

## Repository guide

```text
app.py
requirements.txt
requirements-dev.txt
templates/
static/css/style.css
data/catalog_template.csv
tests/
```

## Project documents

- [Requirements and AI elicitation audit](docs/requirements/requirements-and-ai-elicitation-audit.md)
- [Requirements traceability matrix](docs/requirements/traceability-matrix.md)
- [Domain model](docs/domain-model/domain-model.md)
- [AI critique of the domain model](docs/domain-model/ai-critique.md)
- [ADR-001: Course Data Architecture](docs/adr/ADR-001-course-data-architecture.md)
- [ADR prompt-and-diff log](docs/adr/prompt-and-diff-log.md)
- [Walking Skeleton and CI](docs/walking-skeleton/walking-skeleton.md)
- [Architecture overview](docs/architecture/architecture-overview.md)
- [AI-use disclosure](docs/ai-use/ai-use-disclosure.md)
- [Design walkthrough talking points](docs/presentation/talking-points.md)

## Key architecture decision

The project selects **structured course data with separate student course selections**, rather than hard-coded degree requirements or unrestricted free-form course text. The decision provides consistent course codes, credits, categories, and prerequisite relationships at the cost of added validation, modeling, and data maintenance. See [ADR-001](docs/adr/ADR-001-course-data-architecture.md).

## Known limitations and evidence still needed

1. The seeded catalog and requirement data are prototype examples. They are not authoritative University of Memphis curriculum records.
2. Degree audit results depend on course categories and mappings being accurate; demo data includes a category-based fallback when explicit course-requirement links are absent.
3. The graduation target is stored as student input. Do not represent it as a rigorously verified graduation projection for an official degree plan.
4. The current what-if screen reports direct downstream course dependencies for an action; it does not fully simulate and persist an independent alternate course plan.
5. The priority, auto-plan, and risk logic are simplified, rule-based prototypes and require testing against realistic course plans before relying on them.
6. The source milestone asks for a green CI URL and runtime screenshots/video. The repository now includes tests and CI configuration, but those evidence items must be captured after publishing and running the workflow on GitHub.
7. The AI elicitation audit and domain-model critique in Markdown are consolidated repository versions based on preserved project requirements and artifacts; they are not represented as verbatim transcripts of an unavailable original chat log.

File name: README.md

## GitHub setup

```bash
git init
git add .
git commit -m "Add Tiger Engineering Pathway v3 and project documentation"
git branch -M main
git remote add origin https://github.com/cdcraine/tiger-engineering-pathway.git
git push -u origin main
```

If the repository already exists, inspect its contents before adding the remote or pushing. Do not force-push or overwrite an existing repository history. Keep this repository private until course collaboration, answer-sharing, and university rules have been checked.
