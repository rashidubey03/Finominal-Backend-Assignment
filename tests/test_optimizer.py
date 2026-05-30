import pandas as pd
import pytest

from app.constraints import validate_weight_constraints
from app.optimizer import optimize_weights
from app.portfolio_math import annualized_volatility, portfolio_return_series
from app.schemas import Constraints, Strategy


@pytest.fixture
def returns() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "AAA": [0.01, 0.02, -0.01, 0.01, 0.0, 0.02],
            "BBB": [0.0, 0.005, 0.004, 0.006, -0.002, 0.003],
            "CCC": [0.03, -0.04, 0.02, -0.01, 0.04, -0.02],
        }
    )


def assert_valid_weights(weights: dict[str, float]) -> None:
    assert sum(weights.values()) == pytest.approx(100)
    assert all(weight >= 0 for weight in weights.values())


def test_equal_weights(returns: pd.DataFrame) -> None:
    weights = optimize_weights(Strategy.EQUAL_WEIGHTS, returns, Constraints())

    assert weights == {"AAA": 33.3333333333, "BBB": 33.3333333333, "CCC": 33.3333333334}


def test_minimize_volatility(returns: pd.DataFrame) -> None:
    optimized = optimize_weights(Strategy.MINIMIZE_VOLATILITY, returns, Constraints())
    equal = optimize_weights(Strategy.EQUAL_WEIGHTS, returns, Constraints())

    optimized_returns = portfolio_return_series(returns, optimized)
    equal_returns = portfolio_return_series(returns, equal)

    assert_valid_weights(optimized)
    assert annualized_volatility(optimized_returns) <= annualized_volatility(
        equal_returns
    )


def test_maximize_sharpe(returns: pd.DataFrame) -> None:
    weights = optimize_weights(Strategy.MAXIMIZE_SHARPE, returns, Constraints())

    assert_valid_weights(weights)


def test_risk_parity(returns: pd.DataFrame) -> None:
    weights = optimize_weights(Strategy.RISK_PARITY, returns, Constraints())

    assert_valid_weights(weights)


def test_minimize_drawdown(returns: pd.DataFrame) -> None:
    weights = optimize_weights(Strategy.MINIMIZE_DRAWDOWN, returns, Constraints())

    assert_valid_weights(weights)


def test_strategy_respects_min_max_constraints(returns: pd.DataFrame) -> None:
    constraints = Constraints(min_weight=20, max_weight=50)
    weights = optimize_weights(Strategy.MINIMIZE_VOLATILITY, returns, constraints)

    validate_weight_constraints(weights, constraints)


def test_strategy_respects_min_dividend_yield(returns: pd.DataFrame) -> None:
    weights = optimize_weights(
        Strategy.MAXIMIZE_SHARPE,
        returns,
        Constraints(min_dividend_yield=0.035),
        dividend_yields={"AAA": 0.01, "BBB": 0.04, "CCC": 0.05},
    )

    dividend_yield = sum(
        (weight / 100) * {"AAA": 0.01, "BBB": 0.04, "CCC": 0.05}[ticker]
        for ticker, weight in weights.items()
    )
    assert dividend_yield >= 0.035


def test_optimize_factor_exposure(returns: pd.DataFrame) -> None:
    factors = pd.DataFrame(
        {
            "momentum": returns["AAA"] * 0.5 + returns["CCC"] * 0.1,
            "value": returns["BBB"],
            "size": returns["CCC"],
        }
    )

    weights = optimize_weights(
        Strategy.OPTIMIZE_FACTOR_EXPOSURE,
        returns,
        Constraints(),
        factor_return_matrix=factors,
        factor_target="momentum",
    )

    assert_valid_weights(weights)
