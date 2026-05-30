import pytest
import pandas as pd

from app.data_loader import (
    DataLoadError,
    load_portfolio_data,
    normalize_factor_returns,
    normalize_fund_info,
    require_columns,
    require_sheets,
)


def test_load_portfolio_data() -> None:
    data = load_portfolio_data()

    assert data.tickers == ["AGG", "GLD", "IEFA", "SPY", "VEA"]
    assert data.factors == ["momentum", "size", "value"]
    assert len(data.fund_returns) > 0
    assert len(data.factor_returns) > 0


def test_fund_metadata() -> None:
    metadata = load_portfolio_data().fund_metadata()

    assert metadata["AGG"]["fund_name"] == "iShares Core US Aggregate Bond ETF"
    assert metadata["AGG"]["dividend_yield"] == pytest.approx(0.03974)
    assert metadata["GLD"]["dividend_yield"] is None


def test_return_matrices_align_selected_columns() -> None:
    data = load_portfolio_data()

    fund_matrix = data.fund_return_matrix(["spy", "agg"])
    factor_matrix = data.factor_return_matrix(["Momentum Factor", "Value"])

    assert list(fund_matrix.columns) == ["SPY", "AGG"]
    assert list(factor_matrix.columns) == ["momentum", "value"]
    assert fund_matrix.index.is_monotonic_increasing
    assert factor_matrix.index.is_monotonic_increasing
    assert not fund_matrix.isna().any().any()
    assert not factor_matrix.isna().any().any()


def test_unknown_ticker_raises_error() -> None:
    data = load_portfolio_data()

    with pytest.raises(DataLoadError, match="Unknown tickers"):
        data.fund_return_matrix(["NOPE"])


def test_unknown_factor_raises_error() -> None:
    data = load_portfolio_data()

    with pytest.raises(DataLoadError, match="Unknown factors"):
        data.factor_return_matrix(["NOPE"])


def test_required_sheet_and_column_validation() -> None:
    with pytest.raises(DataLoadError, match="Missing sheets"):
        require_sheets(["Fund Info"])

    with pytest.raises(DataLoadError, match="missing columns"):
        require_columns(pd.DataFrame({"ticker": []}), {"ticker", "fund_name"}, "test")


def test_normalizers_drop_bad_rows() -> None:
    info = normalize_fund_info(
        pd.DataFrame(
            [
                {"ticker": " spy ", "fund_name": " SPY Fund ", "dividend_yield": "0.1"},
                {"ticker": None, "fund_name": "Bad", "dividend_yield": "x"},
            ]
        )
    )
    factors = normalize_factor_returns(
        pd.DataFrame(
            [
                {
                    "date": "2024-01-01",
                    "total_return": "0.01",
                    "index_ticker": "Momentum Factor",
                },
                {"date": None, "total_return": "bad", "index_ticker": "Value"},
            ]
        )
    )

    assert info.to_dict("records") == [
        {"ticker": "SPY", "fund_name": "SPY Fund", "dividend_yield": 0.1}
    ]
    assert factors["factor"].tolist() == ["momentum"]
