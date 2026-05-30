import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_optimize_accepts_valid_contract() -> None:
    response = client.post(
        "/optimize",
        json={
            "holdings": [
                {"ticker": "IEFA", "weight": 25},
                {"ticker": "SPY", "weight": 75},
            ],
            "strategy": "equal_weights",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["optimization_strategy"] == "equal_weights"
    assert body["factor_betas"] is None
    assert set(body["metrics"]) == {
        "expected_return",
        "volatility",
        "sharpe_ratio",
        "max_drawdown",
        "dividend_yield",
    }
    assert body["metrics"]["volatility"] is not None
    assert body["allocation_changes"] == [
        {
            "ticker": "IEFA",
            "security_name": "iShares Core MSCI EAFE ETF",
            "current_weight": 25.0,
            "optimized_weight": 50.0,
            "change": 25.0,
        },
        {
            "ticker": "SPY",
            "security_name": "State Street SPDR S&P 500 ETF Trust",
            "current_weight": 75.0,
            "optimized_weight": 50.0,
            "change": -25.0,
        },
    ]


def test_optimize_runs_non_equal_strategy() -> None:
    response = client.post(
        "/optimize",
        json={
            "holdings": [
                {"ticker": "SPY", "weight": 60},
                {"ticker": "AGG", "weight": 30},
                {"ticker": "GLD", "weight": 10},
            ],
            "strategy": "minimize_volatility",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["optimization_strategy"] == "minimize_volatility"
    optimized_total = sum(
        item["optimized_weight"] for item in body["allocation_changes"]
    )
    assert optimized_total == pytest.approx(100)


def test_optimize_normalizes_strategy_alias_and_ticker() -> None:
    response = client.post(
        "/optimize",
        json={
            "holdings": [
                {"ticker": "agg", "weight": 50},
                {"ticker": "gld", "weight": 50},
            ],
            "strategy": "Equal Weights",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["optimization_strategy"] == "equal_weights"
    assert [item["ticker"] for item in body["allocation_changes"]] == ["AGG", "GLD"]


def test_optimize_rejects_unknown_ticker() -> None:
    response = client.post(
        "/optimize",
        json={
            "holdings": [
                {"ticker": "SPY", "weight": 50},
                {"ticker": "NOPE", "weight": 50},
            ],
            "strategy": "equal_weights",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown tickers: NOPE"


def test_optimize_rejects_weights_not_summing_to_100() -> None:
    response = client.post(
        "/optimize",
        json={
            "holdings": [
                {"ticker": "SPY", "weight": 40},
                {"ticker": "AGG", "weight": 40},
            ],
            "strategy": "equal_weights",
        },
    )

    assert response.status_code == 422
    assert "holding weights must sum to 100" in str(response.json())


def test_optimize_rejects_infeasible_min_weight() -> None:
    response = client.post(
        "/optimize",
        json={
            "holdings": [
                {"ticker": "SPY", "weight": 50},
                {"ticker": "AGG", "weight": 50},
            ],
            "strategy": "equal_weights",
            "constraints": {"min_weight": 60},
        },
    )

    assert response.status_code == 422
    assert "min_weight constraints are infeasible" in str(response.json())


def test_optimize_rejects_unsatisfied_runtime_constraint() -> None:
    response = client.post(
        "/optimize",
        json={
            "holdings": [
                {"ticker": "IEFA", "weight": 25},
                {"ticker": "SPY", "weight": 75},
            ],
            "strategy": "equal_weights",
            "constraints": {"max_drawdown": 0.01},
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "portfolio drawdown exceeds max_drawdown"
