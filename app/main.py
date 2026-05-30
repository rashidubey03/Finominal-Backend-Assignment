from fastapi import FastAPI

from app.api import build_router
from app.data_loader import load_portfolio_data

app = FastAPI(
    title="Portfolio Optimizer API",
    version="0.1.0",
    description="Local REST API for Finominal portfolio optimization assignment.",
)

portfolio_data = load_portfolio_data()
app.include_router(build_router(portfolio_data))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "portfolio-optimizer-api",
        "version": "0.1.0",
    }


@app.get("/data/summary")
def data_summary() -> dict[str, object]:
    return {
        "fund_count": len(portfolio_data.tickers),
        "tickers": portfolio_data.tickers,
        "factors": portfolio_data.factors,
        "fund_return_rows": len(portfolio_data.fund_returns),
        "factor_return_rows": len(portfolio_data.factor_returns),
    }
