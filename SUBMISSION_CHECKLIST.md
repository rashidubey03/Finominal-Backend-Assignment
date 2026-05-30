# Submission Checklist

## Ready

- Source code is in the repository.
- `README.md` includes setup, run, endpoint examples, strategies, assumptions, and tests.
- `Docs/` is ignored because it contains local assignment/context files.
- All required strategies are implemented:
  - `equal_weights`
  - `risk_parity`
  - `minimize_drawdown`
  - `minimize_volatility`
  - `maximize_sharpe`
- Bonus factor exposure is implemented:
  - `optimize_factor_exposure`
  - factor betas for `momentum`, `value`, `size`
- Acceptance scenarios are automated in `tests/test_acceptance_scenarios.py`.

## Verify Before Sending

```bash
python -m pytest
python -m pytest tests/test_acceptance_scenarios.py
uvicorn app.main:app --reload
```

Manual checks:

- Open `http://127.0.0.1:8000/docs`.
- Run at least 3 strategy examples.
- Save screenshots for submission.
- Record 3-5 minute Loom walkthrough.
- Confirm public GitHub repo link is accessible.

