from fastapi import APIRouter, HTTPException

from app.data_loader import PortfolioData
from app.portfolio_math import calculate_metrics, round_weights_to_100
from app.schemas import (
    AllocationChange,
    OptimizeRequest,
    OptimizeResponse,
    PortfolioMetrics,
)


router = APIRouter()


def build_router(data: PortfolioData) -> APIRouter:
    @router.post("/optimize", response_model=OptimizeResponse)
    def optimize_portfolio(request: OptimizeRequest) -> OptimizeResponse:
        tickers = [holding.ticker for holding in request.holdings]
        unknown = sorted(set(tickers).difference(data.tickers))
        if unknown:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown tickers: {', '.join(unknown)}",
            )

        if request.factor_target and request.factor_target not in data.factors:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown factor: {request.factor_target}",
            )

        metadata = data.fund_metadata()
        optimized_weights = equal_weight_allocation(tickers)
        return_matrix = data.fund_return_matrix(tickers)
        metrics = calculate_metrics(return_matrix, optimized_weights, metadata)
        allocation_changes = [
            AllocationChange(
                ticker=holding.ticker,
                security_name=str(metadata[holding.ticker]["fund_name"]),
                current_weight=round(holding.weight, 4),
                optimized_weight=round(optimized_weights[holding.ticker], 4),
                change=round(optimized_weights[holding.ticker] - holding.weight, 4),
            )
            for holding in request.holdings
        ]

        return OptimizeResponse(
            optimization_strategy=request.strategy,
            allocation_changes=allocation_changes,
            metrics=PortfolioMetrics(**metrics),
        )

    return router


def equal_weight_allocation(tickers: list[str]) -> dict[str, float]:
    weight = round(100 / len(tickers), 10)
    weights = {ticker: weight for ticker in tickers}
    return round_weights_to_100(weights, decimals=10)
