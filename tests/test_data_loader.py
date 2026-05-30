import pytest

from app.data_loader import DataLoadError, load_portfolio_data


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

