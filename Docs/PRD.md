# PRD: Portfolio Optimizer API

## 1. Overview
Build a local Python REST API that replicates the core behavior of Finominal's Portfolio Optimizer. The API receives a portfolio, selected optimization strategy, historical return data, and optional constraints, then returns optimized allocation weights.

The project is backend-only. No frontend is required. The main success criterion is that optimized weights closely match the Finominal reference tool for the required scenarios.

## 2. Problem
Portfolio allocation depends on risk, return, drawdown, diversification, constraints, and factor exposure. The assignment asks for an API that automates this optimization using the supplied historical data and returns results in a predictable JSON format.

## 3. Goals
- Provide a clean REST endpoint for portfolio optimization.
- Support five required strategies plus one bonus factor strategy.
- Load and use the provided Excel data.
- Return allocation changes for every selected security.
- Validate inputs and constraints clearly.
- Produce results close to the reference tool.

## 4. Non-Goals
- No frontend UI.
- No authentication.
- No production deployment.
- No real-time market data.
- No database requirement unless helpful.
- No need to exactly reproduce Finominal's internal optimizer beyond assignment tolerance.

## 5. Users
- Evaluator: tests correctness against required scenarios.
- Developer: runs locally and tests via curl/Postman.
- Reviewer: reads code, README, screenshots, and Loom explanation.

## 6. Source Data
File: `Docs/Data.xlsx`

Sheets:
- `Fund Info`: `ticker`, `fund_name`, `dividend_yield`.
- `Fund Returns`: `date`, `total_return`, `ticker`.
- `Factor Returns`: `date`, `total_return`, `index_ticker`.

Expected funds include IEFA, SPY, VEA, AGG, and GLD.

Expected factors include Momentum, Value, and Size.

## 7. Data Handling
- Convert Excel serial dates into normal dates.
- Normalize tickers and strategy names.
- Align selected fund returns by common date range.
- Drop or reject rows with unusable missing values.
- Use only dates available for all selected securities.
- For factor beta calculations, use common dates between portfolio returns and factor returns.

## 8. API Endpoint
Endpoint:

```http
POST /optimize
```

Request shape:

```json
{
  "holdings": [
    { "ticker": "SPY", "weight": 60 },
    { "ticker": "AGG", "weight": 30 },
    { "ticker": "GLD", "weight": 10 }
  ],
  "strategy": "minimize_volatility",
  "constraints": {
    "min_weight": 0,
    "max_weight": 100,
    "min_dividend_yield": null,
    "min_cagr": null,
    "max_drawdown": null,
    "volatility_min": null,
    "volatility_max": null
  },
  "factor_target": null
}
```

Response shape:

```json
{
  "optimization_strategy": "minimize_volatility",
  "allocation_changes": [
    {
      "ticker": "SPY",
      "security_name": "SPDR S&P 500 ETF Trust",
      "current_weight": 60.0,
      "optimized_weight": 42.5,
      "change": -17.5
    }
  ],
  "metrics": {
    "expected_return": 0.0,
    "volatility": 0.0,
    "sharpe_ratio": 0.0,
    "max_drawdown": 0.0,
    "dividend_yield": 0.0
  }
}
```

Bonus response addition:

```json
{
  "factor_betas": {
    "current_portfolio": {
      "value": 0.09,
      "momentum": 0.10,
      "size": 0.12
    },
    "optimized_portfolio": {
      "value": 0.14,
      "momentum": 0.18,
      "size": 0.08
    }
  }
}
```

## 9. Validation
Reject requests when:
- Holdings are empty.
- Ticker is missing or unknown.
- Weight is missing, negative, or non-numeric.
- Current weights do not sum to 100%.
- Strategy is unsupported.
- Constraint values are invalid.
- Min weight total exceeds 100%.
- Max weight total is below 100%.
- Constraints are infeasible.
- Required return data is missing.

Errors should be JSON and human-readable.

## 10. Required Strategies
### 10.1 Equal Weights
Assign equal weight to every selected security. Must sum to 100%.

### 10.2 Risk Parity
Optimize weights so each asset contributes approximately equal portfolio risk. Use historical volatility/covariance.

### 10.3 Minimize Drawdown
Find weights that minimize maximum historical portfolio drawdown over the aligned return window.

### 10.4 Minimize Volatility
Find weights that minimize portfolio standard deviation.

### 10.5 Maximize Sharpe Ratio
Maximize `(portfolio_return - risk_free_rate) / volatility`. Risk-free rate can default to 0%.

### 10.6 Bonus: Optimize Factor Exposure
Maximize or minimize selected factor exposure, especially Momentum, while respecting all weight and portfolio constraints.

## 11. Portfolio Metrics
Calculate at minimum:
- Portfolio return series.
- Annualized return/CAGR.
- Annualized volatility.
- Sharpe ratio.
- Maximum drawdown.
- Weighted dividend yield.
- Factor betas for bonus.

Assume daily returns unless the data proves otherwise. Use consistent annualization, e.g. 252 trading days.

## 12. Constraints
Hard constraints:
- Weights sum to 100%.
- No negative weights.
- Per-security min/max weight.

Optional portfolio constraints:
- Minimum CAGR.
- Volatility range.
- Maximum drawdown.
- Minimum dividend yield.

If constraints cannot be satisfied, return a validation error instead of invalid weights.

## 13. Acceptance Test Scenarios
1. IEFA 25%, SPY 75%; Equal Weights; no constraints.
2. VEA 25%, AGG 75%; Risk Parity; no constraints.
3. SPY 60%, AGG 30%, GLD 10%; Minimize Volatility.
4. IEFA, GLD, AGG, VEA, SPY each 20%; Maximize Sharpe.
5. Same as case 4; Maximize Sharpe; min dividend yield 2.5%; each security min 5%, max 40%.
6. Bonus: same as case 4; Optimize Factor Exposure; maximize Momentum.

Acceptance checks:
- Optimized weights sum to 100%.
- No optimized weight is negative.
- Constraints are respected.
- Required response fields are present.
- Weight differences from reference are under 0.1% where feasible.
- Bonus includes current and optimized factor betas.

## 14. Technical Requirements
- Python backend using FastAPI, Flask, Django, or similar.
- API must run locally.
- README must explain setup and run commands.
- Code should be readable, modular, and reasonably commented.
- Use numeric/scientific libraries where useful, e.g. pandas, numpy, scipy.
- Unit tests are optional but recommended.

## 15. Suggested Architecture
- `main.py` or app entrypoint.
- `schemas.py` for request/response models.
- `data_loader.py` for Excel parsing and normalization.
- `portfolio_math.py` for metrics.
- `optimizer.py` for strategy implementations.
- `factor_model.py` for beta regression.
- `tests/` for validation and strategy tests.

## 16. Deliverables
- Public GitHub repository.
- Source code.
- README with setup, run, and example requests.
- Screenshots proving at least 3 strategies work.
- 3-5 minute Loom explaining code, approach, assumptions, and tradeoffs.

## 17. Evaluation Criteria
- Correctness: 40%.
- Code quality: 30%.
- Communication/Loom: 20%.
- Bonus factor betas: 10%.

## 18. Risks
- Reference tool may use hidden assumptions.
- Optimization may fail for strict constraints.
- Excel date/return formatting may need cleanup.
- Factor beta output may not exactly match due to model differences.

## 19. Assumptions
- Input weights are percentages, not decimals.
- Returns are periodic total returns.
- Risk-free rate defaults to 0%.
- Small floating-point differences are acceptable.
- The API should prefer clear errors over silent fallback behavior.
