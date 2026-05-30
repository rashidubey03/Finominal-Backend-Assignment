# Project Skill: Portfolio Optimizer API

Use these rules for every phase, feature, or fix:

- Start each phase/feature/fix on a new git branch.
- Save all phase/feature/fix context in `Docs/CONTEXT_README.md`.
- Save all test notes in `Docs/TESTS_README.md`.
- Append new sections to those two files; do not create per-phase context/test files.
- Add or update automated tests for every new behavior.
- Commit and push the branch after each completed phase.
- Keep API behavior aligned with `Docs/PRD.md`.
- Keep work phased according to `Docs/IMPLEMENTATION_PLAN.md`.
- Prefer FastAPI, pandas, numpy, scipy, pytest.
- Validate inputs clearly and return JSON errors.
- Keep weights as percentages externally and decimals internally where useful.
- Run relevant tests before finishing.
- Use as less tokens as possible without compromisiing the work as much
