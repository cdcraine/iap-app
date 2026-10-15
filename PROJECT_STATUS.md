# Project Status Checklist

## Included in this GitHub-ready package

- [x] Tiger Engineering Pathway v3 Flask/Jinja source code and catalog CSV template.
- [x] Project README and local-run instructions.
- [x] M2 requirements: eight user stories and acceptance criteria.
- [x] Three measurable non-functional requirements and verification approaches.
- [x] Consolidated AI elicitation audit with human-review notes.
- [x] Domain model, Mermaid class diagram, preserved domain graphic, and critique.
- [x] ADR-001: structured course data with separate student course selections.
- [x] ADR-001 prompt-and-diff log.
- [x] Walking-skeleton description and evidence checklist.
- [x] Student profile data-access helper, pytest tests, and GitHub Actions workflow.
- [x] Basic CSS referenced by the v3 templates.
- [x] `.gitignore` rules for generated databases, Python caches, virtual environments, and `.env` secrets.

## Not yet completed / not claimed

- [ ] Successfully install and run dependencies in this build environment. The environment could not reach the package index, and Flask was not preinstalled.
- [ ] Green GitHub Actions run URL from the actual repository.
- [ ] Fresh browser screenshot/recording of the profile save-and-read-back flow.
- [ ] Performance test evidence for NFR-01 and NFR-02.
- [ ] A 100-case prerequisite correctness test result for NFR-03.
- [ ] Full independent what-if plan and computed graduation-term projection.
- [ ] Validation against authoritative University of Memphis course and degree data.

Before presenting the CI status as green, push this package to GitHub and confirm that the Actions workflow completes successfully. The application code compiles locally in the package build environment, but pytest execution was blocked because the Flask dependency could not be installed without network access.
