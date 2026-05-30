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


def test_submission_checklist_exists() -> None:
    checklist = Path("SUBMISSION_CHECKLIST.md")

    assert checklist.exists()
    text = checklist.read_text(encoding="utf-8")
    assert "python -m pytest" in text
    assert "Loom" in text
    assert "screenshots" in text
