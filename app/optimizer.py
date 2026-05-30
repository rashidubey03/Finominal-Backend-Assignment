import numpy as np
import pandas as pd
from scipy.optimize import minimize

from app.factor_model import target_factor_beta
from app.portfolio_math import (
    annualized_return,
    annualized_volatility,
    max_drawdown,
    portfolio_return_series,
    round_weights_to_100,
    sharpe_ratio,
)
from app.schemas import Constraints, Strategy


class OptimizationError(ValueError):
    """Raised when an optimizer cannot produce valid weights."""


def optimize_weights(
    strategy: Strategy | str,
    return_matrix: pd.DataFrame,
    constraints: Constraints,
    factor_return_matrix: pd.DataFrame | None = None,
    factor_target: str | None = None,
    dividend_yields: dict[str, float] | None = None,
) -> dict[str, float]:
    tickers = list(return_matrix.columns)
    strategy_value = str(strategy)

    if strategy_value == Strategy.EQUAL_WEIGHTS.value:
        return equal_weights(tickers)

    bounds = [(constraints.min_weight / 100, constraints.max_weight / 100)] * len(
        tickers
    )
    initial = initial_guess(len(tickers), bounds)
    scipy_constraints = build_scipy_constraints(
        return_matrix,
        constraints,
        dividend_yields or {},
    )

    if strategy_value == Strategy.MINIMIZE_VOLATILITY.value:
        result = solve(
            return_matrix,
            bounds,
            initial,
            portfolio_volatility_objective,
            scipy_constraints=scipy_constraints,
        )
    elif strategy_value == Strategy.MAXIMIZE_SHARPE.value:
        result = solve(
            return_matrix,
            bounds,
            initial,
            negative_sharpe_objective,
            scipy_constraints=scipy_constraints,
        )
    elif strategy_value == Strategy.RISK_PARITY.value:
        result = solve(
            return_matrix,
            bounds,
            initial,
            risk_parity_objective,
            scipy_constraints=scipy_constraints,
        )
    elif strategy_value == Strategy.MINIMIZE_DRAWDOWN.value:
        result = solve(
            return_matrix,
            bounds,
            initial,
            drawdown_objective,
            scipy_constraints=scipy_constraints,
        )
    elif strategy_value == Strategy.OPTIMIZE_FACTOR_EXPOSURE.value:
        if factor_return_matrix is None or factor_target is None:
            raise OptimizationError("factor_target is required for factor exposure")
        result = solve(
            return_matrix,
            bounds,
            initial,
            negative_factor_exposure_objective,
            factor_return_matrix,
            factor_target,
            scipy_constraints=scipy_constraints,
        )
    else:
        raise OptimizationError(f"Unsupported strategy: {strategy}")

    return vector_to_weights(tickers, result.x)


def equal_weights(tickers: list[str]) -> dict[str, float]:
    weight = 100 / len(tickers)
    return round_weights_to_100({ticker: weight for ticker in tickers}, decimals=10)


def initial_guess(count: int, bounds: list[tuple[float, float]]) -> np.ndarray:
    guess = np.full(count, 1 / count)
    lower = np.array([bound[0] for bound in bounds])
    upper = np.array([bound[1] for bound in bounds])
    clipped = np.clip(guess, lower, upper)
    total = clipped.sum()
    if total <= 0:
        raise OptimizationError("No feasible initial allocation")
    return clipped / total


def solve(
    return_matrix: pd.DataFrame,
    bounds: list[tuple[float, float]],
    initial: np.ndarray,
    objective,
    *extra_args,
    scipy_constraints: list[dict] | None = None,
):
    result = minimize(
        objective,
        initial,
        args=(return_matrix, *extra_args),
        method="SLSQP",
        bounds=bounds,
        constraints=scipy_constraints
        or [{"type": "eq", "fun": lambda weights: np.sum(weights) - 1}],
        options={"maxiter": 1000, "ftol": 1e-12},
    )
    if not result.success:
        raise OptimizationError(result.message)
    return result


def vector_to_weights(tickers: list[str], weights: np.ndarray) -> dict[str, float]:
    percent_weights = {
        ticker: max(float(weight) * 100, 0.0) for ticker, weight in zip(tickers, weights)
    }
    return round_weights_to_100(percent_weights)


def weights_dict(return_matrix: pd.DataFrame, weights: np.ndarray) -> dict[str, float]:
    return {
        ticker: float(weight) * 100
        for ticker, weight in zip(return_matrix.columns, weights)
    }


def portfolio_volatility_objective(
    weights: np.ndarray,
    return_matrix: pd.DataFrame,
) -> float:
    returns = portfolio_return_series(return_matrix, weights_dict(return_matrix, weights))
    return annualized_volatility(returns)


def negative_sharpe_objective(
    weights: np.ndarray,
    return_matrix: pd.DataFrame,
) -> float:
    returns = portfolio_return_series(return_matrix, weights_dict(return_matrix, weights))
    return -sharpe_ratio(returns)


def drawdown_objective(weights: np.ndarray, return_matrix: pd.DataFrame) -> float:
    returns = portfolio_return_series(return_matrix, weights_dict(return_matrix, weights))
    return abs(max_drawdown(returns))


def risk_parity_objective(weights: np.ndarray, return_matrix: pd.DataFrame) -> float:
    covariance = return_matrix.cov().to_numpy() * 252
    portfolio_variance = float(weights.T @ covariance @ weights)
    if portfolio_variance <= 0:
        return 0.0
    marginal_risk = covariance @ weights
    risk_contribution = weights * marginal_risk / np.sqrt(portfolio_variance)
    target = np.full(len(weights), risk_contribution.sum() / len(weights))
    return float(((risk_contribution - target) ** 2).sum())


def portfolio_return_objective(
    weights: np.ndarray,
    return_matrix: pd.DataFrame,
) -> float:
    returns = portfolio_return_series(return_matrix, weights_dict(return_matrix, weights))
    return -annualized_return(returns)


def negative_factor_exposure_objective(
    weights: np.ndarray,
    return_matrix: pd.DataFrame,
    factor_return_matrix: pd.DataFrame,
    factor_target: str,
) -> float:
    exposure = target_factor_beta(
        return_matrix,
        factor_return_matrix,
        weights_dict(return_matrix, weights),
        factor_target,
    )
    return -exposure


def build_scipy_constraints(
    return_matrix: pd.DataFrame,
    constraints: Constraints,
    dividend_yields: dict[str, float],
) -> list[dict]:
    scipy_constraints: list[dict] = [
        {"type": "eq", "fun": lambda weights: np.sum(weights) - 1}
    ]

    if constraints.min_dividend_yield is not None:
        yields = np.array(
            [dividend_yields.get(ticker, 0.0) for ticker in return_matrix.columns]
        )
        scipy_constraints.append(
            {
                "type": "ineq",
                "fun": lambda weights, yields=yields: float(weights @ yields)
                - float(constraints.min_dividend_yield),
            }
        )

    if constraints.min_cagr is not None:
        scipy_constraints.append(
            {
                "type": "ineq",
                "fun": lambda weights: annualized_return(
                    portfolio_return_series(
                        return_matrix,
                        weights_dict(return_matrix, weights),
                    )
                )
                - float(constraints.min_cagr),
            }
        )

    if constraints.volatility_min is not None:
        scipy_constraints.append(
            {
                "type": "ineq",
                "fun": lambda weights: annualized_volatility(
                    portfolio_return_series(
                        return_matrix,
                        weights_dict(return_matrix, weights),
                    )
                )
                - float(constraints.volatility_min),
            }
        )

    if constraints.volatility_max is not None:
        scipy_constraints.append(
            {
                "type": "ineq",
                "fun": lambda weights: float(constraints.volatility_max)
                - annualized_volatility(
                    portfolio_return_series(
                        return_matrix,
                        weights_dict(return_matrix, weights),
                    )
                ),
            }
        )

    if constraints.max_drawdown is not None:
        scipy_constraints.append(
            {
                "type": "ineq",
                "fun": lambda weights: float(constraints.max_drawdown)
                - abs(
                    max_drawdown(
                        portfolio_return_series(
                            return_matrix,
                            weights_dict(return_matrix, weights),
                        )
                    )
                ),
            }
        )

    return scipy_constraints
