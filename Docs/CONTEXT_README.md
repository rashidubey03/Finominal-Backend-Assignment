# Context README

Single source for phase, feature, and fix context. Append new entries here.

## Phase 1: Project Setup

Branch: `phase-1-project-setup`

Goal:
- Create a runnable backend skeleton for the Portfolio Optimizer API.

Scope:
- FastAPI app entrypoint.
- Health endpoint.
- Dependency file.
- Basic README.
- Initial pytest health test.

Out of scope:
- Excel data loading.
- Portfolio math.
- Optimization strategies.
- Constraint engine.

Expected result:
- `uvicorn app.main:app --reload` starts the API.
- `GET /health` returns app status JSON.

## Fix: Shared Context/Test Docs

Branch: `fix-shared-context-test-readmes`

Decision:
- Use this file for all future context updates.
- Use `Docs/TESTS_README.md` for all future test notes.
- Do not create separate `PHASE_<n>_*` docs.

## Phase 2: Data Loading

Branch: `phase-2-data-loading`

Goal:
- Load and normalize `Docs/Data.xlsx` for later portfolio optimization.

Scope:
- Validate required workbook sheets and columns.
- Normalize tickers, factors, dates, and numeric returns.
- Expose fund metadata.
- Build aligned fund and factor return matrices.
- Add a small `/data/summary` endpoint for loader visibility.

Out of scope:
- Optimization request schema.
- Portfolio metrics.
- Strategy implementation.

Expected result:
- App starts after loading workbook.
- Data summary shows 5 funds and 3 factors.

## Process Update: Push After Each Phase

Decision:
- After each phase is completed and tests pass, commit changes and push the phase branch to `origin`.
