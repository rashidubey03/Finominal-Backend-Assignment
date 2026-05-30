# Tests README

Single source for phase, feature, and fix test notes. Append new entries here.

## Phase 1: Project Setup

Automated:
- `tests/test_health.py`
  - Confirms `GET /health` returns HTTP 200.
  - Confirms response has `status=ok`.
  - Confirms response has `service=portfolio-optimizer-api`.

Manual:
- Run server: `uvicorn app.main:app --reload`
- Visit: `http://127.0.0.1:8000/health`

Result:
- `python -m pytest`
- `1 passed, 1 warning`

## Fix: Shared Context/Test Docs

Automated:
- Existing health test still covers app setup.

Manual:
- Confirm `Docs/PHASE_1_CONTEXT.md` and `Docs/PHASE_1_TESTS.md` are removed.
- Confirm context is now in `Docs/CONTEXT_README.md`.
- Confirm test notes are now in `Docs/TESTS_README.md`.

## Phase 2: Data Loading

Automated:
- `tests/test_data_loader.py`
  - Confirms workbook loads.
  - Confirms expected tickers and factors.
  - Confirms fund metadata includes names and dividend yield.
  - Confirms fund/factor matrices align by date and contain selected columns.
  - Confirms unknown tickers raise `DataLoadError`.
- `tests/test_health.py`
  - Confirms `/data/summary` returns 5 funds and 3 factors.

Manual:
- Run server: `uvicorn app.main:app --reload`
- Visit: `http://127.0.0.1:8000/data/summary`

