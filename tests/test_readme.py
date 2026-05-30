from pathlib import Path


def test_readme_contains_evaluator_sections() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for section in [
        "## Setup",
        "## Run",
        "## Main Endpoint",
        "## Strategies",
        "## Constraints",
        "## Tests",
        "## Assignment Scenarios",
        "## Assumptions",
        "## Known Limitations",
    ]:
        assert section in readme


def test_readme_mentions_required_strategies() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for strategy in [
        "equal_weights",
        "risk_parity",
        "minimize_drawdown",
        "minimize_volatility",
        "maximize_sharpe",
        "optimize_factor_exposure",
    ]:
        assert strategy in readme


def test_swagger_runs_readme_exists() -> None:
    swagger_runs = Path("SWAGGER_RUNS.md")

    assert swagger_runs.exists()
    text = swagger_runs.read_text(encoding="utf-8")
    assert "400 Bad Request" in text
    assert "minimize_volatility" in text
    assert "optimize_factor_exposure" in text
