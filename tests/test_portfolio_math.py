import pandas as pd
import pytest

from app.portfolio_math import (
    annualized_return,
    annualized_volatility,
    calculate_metrics,
    max_drawdown,
    portfolio_return_series,
    round_weights_to_100,
    sharpe_ratio,
    weighted_dividend_yield,
)


def test_portfolio_return_series() -> None:
    returns = pd.DataFrame({"AAA": [0.1, 0.0], "BBB": [0.0, 0.2]})

    result = portfolio_return_series(returns, {"AAA": 50, "BBB": 50})

    assert result.tolist() == pytest.approx([0.05, 0.1])


def test_core_metrics() -> None:
    returns = pd.Series([0.01, -0.02, 0.03, -0.01])

    assert annualized_return(returns) != 0
    assert annualized_volatility(returns) > 0
    assert sharpe_ratio(returns) != 0
    assert max_drawdown(returns) == pytest.approx(-0.02)


def test_weighted_dividend_yield() -> None:
    metadata = {
        "AAA": {"fund_name": "A", "dividend_yield": 0.04},
        "BBB": {"fund_name": "B", "dividend_yield": None},
    }

    assert weighted_dividend_yield({"AAA": 25, "BBB": 75}, metadata) == pytest.approx(
        0.01
    )


def test_calculate_metrics_shape() -> None:
    returns = pd.DataFrame({"AAA": [0.01, 0.02, -0.01], "BBB": [0.0, 0.01, 0.01]})
    metadata = {
        "AAA": {"fund_name": "A", "dividend_yield": 0.04},
        "BBB": {"fund_name": "B", "dividend_yield": 0.02},
    }

    metrics = calculate_metrics(returns, {"AAA": 50, "BBB": 50}, metadata)

    assert set(metrics) == {
        "expected_return",
        "volatility",
        "sharpe_ratio",
        "max_drawdown",
        "dividend_yield",
    }
    assert metrics["dividend_yield"] == pytest.approx(0.03)


def test_round_weights_to_100() -> None:
    weights = round_weights_to_100({"AAA": 33.33333, "BBB": 33.33333, "CCC": 33.33333})

    assert sum(weights.values()) == pytest.approx(100)
    assert weights["CCC"] == pytest.approx(33.3334)

