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

