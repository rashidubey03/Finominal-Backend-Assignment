# Swagger Run Results

These are the local Swagger checks run from:

```text
http://127.0.0.1:8000/docs
```

Endpoint:

```http
POST /optimize
```

## 1. Constraint Validation Error

This run intentionally shows validation behavior when constraints cannot be satisfied.

Request:

```json
{
  "holdings": [
    { "ticker": "SPY", "weight": 60 },
    { "ticker": "AGG", "weight": 30 },
    { "ticker": "GLD", "weight": 10 }
  ],
  "strategy": "equal_weights",
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

Observed response:

```json
{
  "detail": "portfolio dividend yield is below min_dividend_yield"
}
```

Status:

```text
400 Bad Request
```

Why this matters:

- Confirms portfolio-level constraints are validated.
- Confirms the API returns a clear JSON error instead of invalid weights.

## 2. Minimize Volatility Success

Request:

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

Observed response summary:

```json
{
  "optimization_strategy": "minimize_volatility",
  "allocation_changes": [
    {
      "ticker": "SPY",
      "current_weight": 60,
      "optimized_weight": 6.923,
      "change": -53.077
    },
    {
      "ticker": "AGG",
      "current_weight": 30,
      "optimized_weight": 91.2122,
      "change": 61.2122
    },
    {
      "ticker": "GLD",
      "current_weight": 10,
      "optimized_weight": 1.8648,
      "change": -8.1352
    }
  ],
  "metrics": {
    "expected_return": 0.038744
  }
}
```

Status:

```text
200 OK
```

Why this matters:

- Confirms a required optimization strategy runs successfully.
- Confirms optimized weights are returned per ticker.
- Confirms metrics are included in the response.

## 3. Bonus Factor Exposure Success

Request:

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

Observed response:

```text
200 OK
```

Response includes:

- `allocation_changes`
- `metrics`
- `factor_betas.current_portfolio`
- `factor_betas.optimized_portfolio`

Why this matters:

- Confirms the bonus strategy runs through Swagger.
- Confirms the API returns factor beta data for Momentum, Value, and Size.

## Notes

- Screenshots were captured from Swagger after executing the JSON requests above.
- The exact numeric values can change if optimizer logic, data, or constraints change.
- The important checks are status code, valid JSON response shape, weights summing to `100`, metrics presence, and factor beta presence for the bonus case.
