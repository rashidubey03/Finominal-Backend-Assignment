import pytest
from pydantic import ValidationError

from app.schemas import Constraints, OptimizeRequest, Strategy


def test_strategy_aliases_normalize() -> None:
    request = OptimizeRequest(
        holdings=[
            {"ticker": "spy", "weight": 50},
            {"ticker": "agg", "weight": 50},
        ],
        strategy="Maximize Sharpe Ratio",
    )

    assert request.strategy == Strategy.MAXIMIZE_SHARPE.value
    assert [holding.ticker for holding in request.holdings] == ["SPY", "AGG"]


def test_duplicate_tickers_rejected() -> None:
    with pytest.raises(ValidationError, match="duplicate tickers"):
        OptimizeRequest(
            holdings=[
                {"ticker": "SPY", "weight": 50},
                {"ticker": "spy", "weight": 50},
            ],
            strategy="equal_weights",
        )


def test_bad_strategy_rejected() -> None:
    with pytest.raises(ValidationError, match="Unsupported strategy"):
        OptimizeRequest(
            holdings=[{"ticker": "SPY", "weight": 100}],
            strategy="not_real",
        )


def test_constraint_ranges_rejected() -> None:
    with pytest.raises(ValidationError, match="min_weight cannot exceed max_weight"):
        Constraints(min_weight=60, max_weight=40)

    with pytest.raises(
        ValidationError,
        match="volatility_min cannot exceed volatility_max",
    ):
        Constraints(volatility_min=0.2, volatility_max=0.1)

