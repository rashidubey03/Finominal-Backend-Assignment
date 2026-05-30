import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.acceptance_cases import ACCEPTANCE_CASES


client = TestClient(app)


@pytest.mark.parametrize("case", ACCEPTANCE_CASES, ids=[case["name"] for case in ACCEPTANCE_CASES])
def test_acceptance_case(case: dict) -> None:
    response = client.post("/optimize", json=case["payload"])

    assert response.status_code == 200
    body = response.json()
    assert body["optimization_strategy"] == case["payload"]["strategy"]
    assert_valid_response(body, case["payload"])

    if case["requires_factor_betas"]:
        assert body["factor_betas"] is not None
        assert set(body["factor_betas"]["current_portfolio"]) == {
            "momentum",
            "value",
            "size",
        }
        assert set(body["factor_betas"]["optimized_portfolio"]) == {
            "momentum",
            "value",
            "size",
        }
    else:
        assert body["factor_betas"] is None


def assert_valid_response(body: dict, payload: dict) -> None:
    allocations = body["allocation_changes"]
    constraints = payload.get("constraints", {})
    min_weight = constraints.get("min_weight", 0)
    max_weight = constraints.get("max_weight", 100)

    assert len(allocations) == len(payload["holdings"])
    assert sum(row["optimized_weight"] for row in allocations) == pytest.approx(
        100,
        abs=0.001,
    )

    for row in allocations:
        assert row["ticker"] in {holding["ticker"] for holding in payload["holdings"]}
        assert row["security_name"]
        assert row["optimized_weight"] >= min_weight - 0.001
        assert row["optimized_weight"] <= max_weight + 0.001
        assert row["optimized_weight"] >= 0

    assert set(body["metrics"]) == {
        "expected_return",
        "volatility",
        "sharpe_ratio",
        "max_drawdown",
        "dividend_yield",
    }

