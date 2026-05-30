# Implementation Plan

## Phase 1: Project Setup
Goal: create a runnable backend skeleton.

Tasks:
- Choose FastAPI unless there is a reason to use another framework.
- Create app structure: app entrypoint, schemas, services, tests.
- Add dependencies: fastapi, uvicorn, pandas, openpyxl, numpy, scipy, pytest.
- Add `.gitignore` and README starter.
- Add health endpoint, e.g. `GET /health`.

Done when:
- Server runs locally.
- README has setup and run commands.

## Phase 2: Data Loading
Goal: reliably load `Docs/Data.xlsx`.

Tasks:
- Read `Fund Info`, `Fund Returns`, and `Factor Returns`.
- Convert Excel dates.
- Normalize tickers and factor names.
- Validate required columns.
- Build fund metadata lookup.
- Build aligned fund return matrix.
- Build aligned factor return matrix.

Done when:
- Data loads at startup or first request.
- Invalid/missing sheet/column errors are clear.

## Phase 3: API Contract
Goal: implement stable input/output models.

Tasks:
- Define request schema: holdings, strategy, constraints, factor target.
- Define response schema: allocation changes, metrics, optional factor betas.
- Normalize strategy aliases.
- Validate weights sum to 100%.
- Validate ticker existence.
- Validate constraint feasibility basics.

Done when:
- `POST /optimize` accepts valid JSON.
- Invalid requests return clear JSON errors.

## Phase 4: Portfolio Math
Goal: build reusable calculations.

Tasks:
- Compute weighted portfolio return series.
- Compute annualized return/CAGR.
- Compute annualized volatility.
- Compute Sharpe ratio with risk-free rate default 0%.
- Compute cumulative returns and max drawdown.
- Compute weighted dividend yield.
- Add helper to round final weights while preserving 100%.

Done when:
- Metrics are tested with small known inputs.

## Phase 5: Constraint Engine
Goal: centralize optimization constraints.

Tasks:
- Implement sum-to-100 constraint.
- Implement no-short constraint.
- Implement per-security min/max constraints.
- Implement portfolio-level constraints:
  - min CAGR
  - volatility min/max
  - max drawdown
  - min dividend yield
- Return infeasible constraint errors.

Done when:
- All strategies use the same constraint helpers.

## Phase 6: Required Strategies
Goal: implement assignment strategies in priority order.

Tasks:
- Equal Weights: deterministic baseline.
- Minimize Volatility: scipy constrained minimization.
- Maximize Sharpe: minimize negative Sharpe.
- Risk Parity: minimize risk contribution differences.
- Minimize Drawdown: minimize historical max drawdown.

Done when:
- Each strategy returns valid weights.
- Weights sum to 100% and respect constraints.

## Phase 7: Bonus Factor Exposure
Goal: implement optional factor optimization.

Tasks:
- Compute portfolio return series.
- Align portfolio returns with factor returns.
- Run regression against Momentum, Value, Size.
- Return current and optimized factor betas.
- Add objective to maximize selected factor, especially Momentum.

Done when:
- Case 6 returns higher Momentum exposure where feasible.
- Response includes `factor_betas`.

## Phase 8: Acceptance Scenarios
Goal: verify against PRD cases.

Tasks:
- Create example JSON for all 6 cases.
- Run each through local API.
- Compare output with Finominal tool.
- Adjust assumptions if weights differ materially.
- Keep screenshots for at least 3 strategies.

Done when:
- Cases 1-5 pass core checks.
- Case 6 passes bonus checks if implemented.

## Phase 9: Tests
Goal: protect core behavior.

Tasks:
- Unit tests for data loading.
- Unit tests for metrics.
- Unit tests for validation errors.
- Unit tests for each strategy's basic invariants.
- API tests for success and failure responses.

Done when:
- `pytest` runs locally.
- Critical math and validation paths are covered.

## Phase 10: Documentation
Goal: make the project easy to evaluate.

Tasks:
- Finish README with:
  - setup
  - run command
  - endpoint docs
  - request/response examples
  - assumptions
  - known limitations
- Include strategy descriptions.
- Include screenshots.
- Mention tolerance and validation rules.

Done when:
- A reviewer can run the API from README alone.

## Phase 11: Final Submission
Goal: package deliverables.

Tasks:
- Clean repo.
- Run tests.
- Run all acceptance examples.
- Record 3-5 minute Loom.
- Push public GitHub repo.

Done when:
- Repo link, screenshots, and Loom are ready.

## Suggested Build Order
1. Equal Weights API end-to-end.
2. Data loader and response formatting.
3. Metrics.
4. Min Volatility.
5. Max Sharpe.
6. Risk Parity.
7. Min Drawdown.
8. Constraints.
9. Bonus factor exposure.
10. Tests and docs.

## Key Risks
- Exact reference outputs may depend on hidden Finominal assumptions.
- Some constraint combinations may be infeasible.
- Drawdown optimization can be slower or less stable.
- Factor beta comparison may differ from the live tool's broader model.
