import pandas as pd
import pytest

from app.factor_model import calculate_factor_betas, target_factor_beta


def test_calculate_factor_betas() -> None:
    factors = pd.DataFrame(
        {
            "momentum": [0.01, 0.02, -0.01, 0.0],
            "value": [0.0, 0.01, 0.0, -0.01],
            "size": [0.02, 0.0, 0.01, -0.02],
        }
    )
    funds = pd.DataFrame(
        {
            "AAA": 2 * factors["momentum"] + 0.5 * factors["value"],
            "BBB": factors["size"],
        }
    )

    betas = calculate_factor_betas(funds, factors, {"AAA": 100, "BBB": 0})

    assert betas["momentum"] == pytest.approx(2, abs=1e-6)
    assert betas["value"] == pytest.approx(0.5, abs=1e-6)


def test_target_factor_beta() -> None:
    factors = pd.DataFrame({"momentum": [0.01, 0.02, -0.01], "value": [0, 0, 0]})
    funds = pd.DataFrame({"AAA": [0.02, 0.04, -0.02]})

    assert target_factor_beta(funds, factors, {"AAA": 100}, "momentum") == pytest.approx(
        2,
        abs=1e-6,
    )

