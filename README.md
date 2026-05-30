# Finominal Portfolio Optimizer API

Backend assignment implementation for a local portfolio optimization REST API.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Test

```bash
pytest
```

## Acceptance Scenarios

The required assignment scenarios are covered in:

```bash
python -m pytest tests/test_acceptance_scenarios.py
```

They validate all five required strategies plus the bonus factor exposure case.

