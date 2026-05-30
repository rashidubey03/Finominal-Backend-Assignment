"""Factor beta regression helpers for Momentum, Value, and Size exposure."""

import numpy as np
import pandas as pd

from app.portfolio_math import portfolio_return_series


DEFAULT_FACTORS = ["momentum", "value", "size"]


def calculate_factor_betas(
    fund_return_matrix: pd.DataFrame,
    factor_return_matrix: pd.DataFrame,
    weights: dict[str, float],
) -> dict[str, float]:
    portfolio_returns = portfolio_return_series(fund_return_matrix, weights)
    aligned = pd.concat([portfolio_returns.rename("portfolio"), factor_return_matrix], axis=1).dropna()
    if aligned.empty:
        return {factor: 0.0 for factor in factor_return_matrix.columns}

    y = aligned["portfolio"].to_numpy()
    x = aligned[factor_return_matrix.columns].to_numpy()
    x = np.column_stack([np.ones(len(x)), x])
    coefficients = np.linalg.lstsq(x, y, rcond=None)[0]

    return {
        factor: round(float(beta), 6)
        for factor, beta in zip(factor_return_matrix.columns, coefficients[1:])
    }


def target_factor_beta(
    fund_return_matrix: pd.DataFrame,
    factor_return_matrix: pd.DataFrame,
    weights: dict[str, float],
    factor_target: str,
) -> float:
    betas = calculate_factor_betas(fund_return_matrix, factor_return_matrix, weights)
    return betas.get(factor_target, 0.0)
