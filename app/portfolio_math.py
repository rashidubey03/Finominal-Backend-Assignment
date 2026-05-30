"""Reusable portfolio return, risk, drawdown, and yield calculations."""

import math

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def weights_to_decimal(weights: dict[str, float]) -> pd.Series:
    return pd.Series(weights, dtype=float) / 100


def portfolio_return_series(
    return_matrix: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    decimals = weights_to_decimal(weights)
    aligned = return_matrix[decimals.index]
    return aligned.mul(decimals, axis="columns").sum(axis="columns")


def annualized_return(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    clean = returns.dropna()
    if clean.empty:
        return 0.0
    cumulative = float((1 + clean).prod())
    years = len(clean) / periods_per_year
    if years <= 0 or cumulative <= 0:
        return 0.0
    return cumulative ** (1 / years) - 1


def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    clean = returns.dropna()
    if len(clean) < 2:
        return 0.0
    return float(clean.std(ddof=1) * math.sqrt(periods_per_year))


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> float:
    volatility = annualized_volatility(returns, periods_per_year)
    if volatility == 0:
        return 0.0
    return (annualized_return(returns, periods_per_year) - risk_free_rate) / volatility


def max_drawdown(returns: pd.Series) -> float:
    clean = returns.dropna()
    if clean.empty:
        return 0.0
    cumulative = (1 + clean).cumprod()
    running_max = cumulative.cummax()
    drawdowns = cumulative / running_max - 1
    return float(drawdowns.min())


def weighted_dividend_yield(
    weights: dict[str, float],
    metadata: dict[str, dict[str, float | str | None]],
) -> float:
    total = 0.0
    for ticker, weight in weights.items():
        dividend_yield = metadata[ticker]["dividend_yield"]
        if dividend_yield is not None:
            total += (weight / 100) * float(dividend_yield)
    return total


def calculate_metrics(
    return_matrix: pd.DataFrame,
    weights: dict[str, float],
    metadata: dict[str, dict[str, float | str | None]],
) -> dict[str, float]:
    returns = portfolio_return_series(return_matrix, weights)
    return {
        "expected_return": round(annualized_return(returns), 6),
        "volatility": round(annualized_volatility(returns), 6),
        "sharpe_ratio": round(sharpe_ratio(returns), 6),
        "max_drawdown": round(max_drawdown(returns), 6),
        "dividend_yield": round(weighted_dividend_yield(weights, metadata), 6),
    }


def round_weights_to_100(weights: dict[str, float], decimals: int = 4) -> dict[str, float]:
    rounded = {ticker: round(weight, decimals) for ticker, weight in weights.items()}
    diff = round(100 - sum(rounded.values()), decimals)
    if rounded:
        last_ticker = next(reversed(rounded))
        rounded[last_ticker] = round(rounded[last_ticker] + diff, decimals)
    return rounded


def covariance_matrix(return_matrix: pd.DataFrame) -> np.ndarray:
    return return_matrix.cov().to_numpy() * TRADING_DAYS
