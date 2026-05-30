from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Strategy(StrEnum):
    EQUAL_WEIGHTS = "equal_weights"
    RISK_PARITY = "risk_parity"
    MINIMIZE_DRAWDOWN = "minimize_drawdown"
    MINIMIZE_VOLATILITY = "minimize_volatility"
    MAXIMIZE_SHARPE = "maximize_sharpe"
    OPTIMIZE_FACTOR_EXPOSURE = "optimize_factor_exposure"


STRATEGY_ALIASES = {
    "equal weights": Strategy.EQUAL_WEIGHTS,
    "equal_weights": Strategy.EQUAL_WEIGHTS,
    "risk parity": Strategy.RISK_PARITY,
    "risk_parity": Strategy.RISK_PARITY,
    "minimize drawdown": Strategy.MINIMIZE_DRAWDOWN,
    "minimize_drawdown": Strategy.MINIMIZE_DRAWDOWN,
    "minimize volatility": Strategy.MINIMIZE_VOLATILITY,
    "minimize_volatility": Strategy.MINIMIZE_VOLATILITY,
    "maximize sharpe": Strategy.MAXIMIZE_SHARPE,
    "maximize sharpe ratio": Strategy.MAXIMIZE_SHARPE,
    "maximize_sharpe": Strategy.MAXIMIZE_SHARPE,
    "optimize factor exposure": Strategy.OPTIMIZE_FACTOR_EXPOSURE,
    "optimize_factor_exposure": Strategy.OPTIMIZE_FACTOR_EXPOSURE,
}


class Holding(BaseModel):
    ticker: str = Field(..., min_length=1)
    weight: float = Field(..., ge=0, le=100)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.upper().strip()


class Constraints(BaseModel):
    min_weight: float = Field(default=0, ge=0, le=100)
    max_weight: float = Field(default=100, ge=0, le=100)
    min_dividend_yield: float | None = Field(default=None, ge=0)
    min_cagr: float | None = None
    max_drawdown: float | None = Field(default=None, ge=0)
    volatility_min: float | None = Field(default=None, ge=0)
    volatility_max: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_ranges(self) -> "Constraints":
        if self.min_weight > self.max_weight:
            raise ValueError("min_weight cannot exceed max_weight")
        if (
            self.volatility_min is not None
            and self.volatility_max is not None
            and self.volatility_min > self.volatility_max
        ):
            raise ValueError("volatility_min cannot exceed volatility_max")
        return self


class OptimizeRequest(BaseModel):
    holdings: list[Holding] = Field(..., min_length=1)
    strategy: Strategy
    constraints: Constraints = Field(default_factory=Constraints)
    factor_target: str | None = None

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("strategy", mode="before")
    @classmethod
    def normalize_strategy(cls, value: str | Strategy) -> Strategy:
        if isinstance(value, Strategy):
            return value
        key = str(value).strip().lower().replace("-", "_")
        if key not in STRATEGY_ALIASES:
            raise ValueError(f"Unsupported strategy: {value}")
        return STRATEGY_ALIASES[key]

    @field_validator("factor_target")
    @classmethod
    def normalize_factor_target(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower().replace(" factor", "")

    @model_validator(mode="after")
    def validate_holdings(self) -> "OptimizeRequest":
        tickers = [holding.ticker for holding in self.holdings]
        if len(tickers) != len(set(tickers)):
            raise ValueError("holdings cannot contain duplicate tickers")

        total_weight = sum(holding.weight for holding in self.holdings)
        if abs(total_weight - 100) > 0.001:
            raise ValueError("holding weights must sum to 100")

        count = len(self.holdings)
        if self.constraints.min_weight * count > 100:
            raise ValueError("min_weight constraints are infeasible")
        if self.constraints.max_weight * count < 100:
            raise ValueError("max_weight constraints are infeasible")
        return self


class AllocationChange(BaseModel):
    ticker: str
    security_name: str
    current_weight: float
    optimized_weight: float
    change: float


class PortfolioMetrics(BaseModel):
    expected_return: float | None = None
    volatility: float | None = None
    sharpe_ratio: float | None = None
    max_drawdown: float | None = None
    dividend_yield: float | None = None


class FactorBetas(BaseModel):
    current_portfolio: dict[str, float]
    optimized_portfolio: dict[str, float]


class OptimizeResponse(BaseModel):
    optimization_strategy: Strategy
    allocation_changes: list[AllocationChange]
    metrics: PortfolioMetrics = Field(default_factory=PortfolioMetrics)
    factor_betas: FactorBetas | None = None

    model_config = ConfigDict(use_enum_values=True)
