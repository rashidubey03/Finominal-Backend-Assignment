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


def test_swagger_results_docx_exists() -> None:
    swagger_results = Path("Swagger_Test_Results.docx")

    assert swagger_results.exists()
    assert swagger_results.stat().st_size > 0
