# Upload M7 Refactoring Submission to GitHub

1. Extract this ZIP.
2. Open Terminal in `Tiger-Engineering-Pathway-v3`.
3. Install dependencies and verify tests:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_planning_logic.py
python -m pytest -q
```

4. Inspect the full package and `git status --short`. If this folder is already a clone of your project repository, add and commit the M7 files. If it is not a clone, connect it only after confirming the target repository and remote; do not force-push over existing history.
5. The M7 report is `Tiger_Engineering_Pathway_M7_Refactoring_Report.docx` and is also saved under `Tiger-Engineering-Pathway-v3/docs/assignment/`. Appendix A now contains dashboard, course-priority, and student-setup interface previews. The full set is in `Tiger-Engineering-Pathway-v3/docs/figures/`.

Recorded targeted tests: 6 passed before and 6 passed after, using the same unchanged test file. The full suite needs a dependency-enabled run because Flask could not be installed in the authoring environment.
