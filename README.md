# Finominal Portfolio Optimizer API

Local Python REST API for the Finominal backend assignment. It loads the provided Excel workbook, optimizes portfolio weights, and returns allocation changes, metrics, and optional factor betas.

## Tech Stack

- Python
- FastAPI
- pandas / openpyxl
- numpy / scipy
- pytest

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

Open Swagger docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Data summary:

```bash
curl http://127.0.0.1:8000/data/summary
```

## Main Endpoint

```http
POST /optimize
```

Example:

```json
{
  "holdings": [
    { "ticker": "SPY", "weight": 60 },
    { "ticker": "AGG", "weight": 30 },
    { "ticker": "GLD", "weight": 10 }
  ],
  "strategy": "minimize_volatility"
}
```

Response includes:

- `optimization_strategy`
- `allocation_changes`
- `metrics`
- `factor_betas` for factor exposure strategy

## Strategies

- `equal_weights`
- `risk_parity`
- `minimize_drawdown`
- `minimize_volatility`
- `maximize_sharpe`
- `optimize_factor_exposure`

## Constraints

Optional request constraints:

```json
{
  "constraints": {
    "min_weight": 5,
    "max_weight": 40,
    "min_dividend_yield": 0.025,
    "min_cagr": null,
    "max_drawdown": null,
    "volatility_min": null,
    "volatility_max": null
  }
}
```

Rules:

- Input weights must sum to `100`.
- Optimized weights sum to `100`.
- No short selling.
- Min/max security weights are enforced.
- Portfolio constraints return clear errors if infeasible.

## Bonus Factor Exposure

Example:

```json
{
  "holdings": [
    { "ticker": "IEFA", "weight": 20 },
    { "ticker": "GLD", "weight": 20 },
    { "ticker": "AGG", "weight": 20 },
    { "ticker": "VEA", "weight": 20 },
    { "ticker": "SPY", "weight": 20 }
  ],
  "strategy": "optimize_factor_exposure",
  "factor_target": "momentum"
}
```

Returns current and optimized betas for:

- `momentum`
- `value`
- `size`

## Tests

Run all tests:

```bash
python -m pytest
```

Run acceptance scenarios:

```bash
python -m pytest tests/test_acceptance_scenarios.py
```

Current coverage includes:

- Data loading
- Schema validation
- Portfolio math
- Constraint validation
- Required optimizers
- Factor betas
- API responses
- Six assignment acceptance scenarios

## Assignment Scenarios

The six required scenarios are stored in:

```text
tests/acceptance_cases.py
```

They cover:

- Equal Weights
- Risk Parity
- Minimize Volatility
- Maximize Sharpe
- Constrained Maximize Sharpe
- Bonus Momentum factor exposure

## Assumptions

- Weights in API requests/responses are percentages.
- Return data is treated as daily total returns.
- Annualization uses `252` trading days.
- Risk-free rate defaults to `0`.
- Missing dividend yields are treated as `0` for constraint math.
- Factor exposure uses linear regression against Momentum, Value, and Size.

## Known Limitations

- Results may differ from Finominal's live tool because its internal optimizer/model assumptions are not public.
- Portfolio-level constraints are enforced through scipy SLSQP and may fail if infeasible.
- No frontend, auth, database, deployment, or live market data.
- `Docs/` is intentionally ignored and not pushed because it contains local assignment/context files.

