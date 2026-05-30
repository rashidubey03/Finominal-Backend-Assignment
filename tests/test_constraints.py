import pytest

from app.constraints import (
    ConstraintViolation,
    validate_all_constraints,
    validate_metric_constraints,
    validate_weight_constraints,
)
from app.schemas import Constraints


BASE_METRICS = {
    "expected_return": 0.08,
    "volatility": 0.12,
    "sharpe_ratio": 0.66,
    "max_drawdown": -0.2,
    "dividend_yield": 0.03,
}


def test_weight_constraints_accept_valid_weights() -> None:
    validate_weight_constraints(
        {"AAA": 40, "BBB": 60},
        Constraints(min_weight=20, max_weight=80),
    )


def test_weight_constraints_reject_bad_sum() -> None:
    with pytest.raises(ConstraintViolation, match="sum to 100"):
        validate_weight_constraints({"AAA": 40, "BBB": 50}, Constraints())


def test_weight_constraints_reject_min_max_violations() -> None:
    with pytest.raises(ConstraintViolation, match="below min_weight"):
        validate_weight_constraints({"AAA": 10, "BBB": 90}, Constraints(min_weight=20))

    with pytest.raises(ConstraintViolation, match="exceeds max_weight"):
        validate_weight_constraints({"AAA": 80, "BBB": 20}, Constraints(max_weight=70))


def test_metric_constraints_accept_valid_metrics() -> None:
    validate_metric_constraints(
        BASE_METRICS,
        Constraints(
            min_cagr=0.05,
            volatility_min=0.1,
            volatility_max=0.2,
            max_drawdown=0.25,
            min_dividend_yield=0.02,
        ),
    )


def test_metric_constraints_reject_portfolio_violations() -> None:
    cases = [
        (Constraints(min_cagr=0.1), "below min_cagr"),
        (Constraints(volatility_min=0.2), "below volatility_min"),
        (Constraints(volatility_max=0.1), "exceeds volatility_max"),
        (Constraints(max_drawdown=0.1), "exceeds max_drawdown"),
        (Constraints(min_dividend_yield=0.04), "below min_dividend_yield"),
    ]

    for constraints, message in cases:
        with pytest.raises(ConstraintViolation, match=message):
            validate_metric_constraints(BASE_METRICS, constraints)


def test_validate_all_constraints() -> None:
    validate_all_constraints(
        {"AAA": 50, "BBB": 50},
        BASE_METRICS,
        Constraints(min_weight=40, max_weight=60, min_cagr=0.05),
    )

