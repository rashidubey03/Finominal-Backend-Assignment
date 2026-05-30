from fastapi import APIRouter, HTTPException

from app.constraints import ConstraintViolation, validate_all_constraints
from app.data_loader import PortfolioData
from app.optimizer import OptimizationError, optimize_weights
from app.portfolio_math import calculate_metrics
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

        return_matrix = data.fund_return_matrix(tickers)
        metadata = data.fund_metadata()
        try:
            optimized_weights = optimize_weights(
                request.strategy,
                return_matrix,
                request.constraints,
            )
        except OptimizationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        metrics = calculate_metrics(return_matrix, optimized_weights, metadata)
        try:
            validate_all_constraints(optimized_weights, metrics, request.constraints)
        except ConstraintViolation as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

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
