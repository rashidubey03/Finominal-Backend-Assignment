from app.schemas import Constraints


class ConstraintViolation(ValueError):
    """Raised when an allocation fails requested portfolio constraints."""


def validate_weight_constraints(
    weights: dict[str, float],
    constraints: Constraints,
    tolerance: float = 0.001,
) -> None:
    total_weight = sum(weights.values())
    if abs(total_weight - 100) > tolerance:
        raise ConstraintViolation("optimized weights must sum to 100")

    for ticker, weight in weights.items():
        if weight < -tolerance:
            raise ConstraintViolation(f"{ticker} weight cannot be negative")
        if weight + tolerance < constraints.min_weight:
            raise ConstraintViolation(
                f"{ticker} weight is below min_weight {constraints.min_weight}"
            )
        if weight - tolerance > constraints.max_weight:
            raise ConstraintViolation(
                f"{ticker} weight exceeds max_weight {constraints.max_weight}"
            )


def validate_metric_constraints(
    metrics: dict[str, float],
    constraints: Constraints,
    tolerance: float = 1e-9,
) -> None:
    if (
        constraints.min_cagr is not None
        and metrics["expected_return"] + tolerance < constraints.min_cagr
    ):
        raise ConstraintViolation("portfolio return is below min_cagr")

    if (
        constraints.volatility_min is not None
        and metrics["volatility"] + tolerance < constraints.volatility_min
    ):
        raise ConstraintViolation("portfolio volatility is below volatility_min")

    if (
        constraints.volatility_max is not None
        and metrics["volatility"] - tolerance > constraints.volatility_max
    ):
        raise ConstraintViolation("portfolio volatility exceeds volatility_max")

    if constraints.max_drawdown is not None:
        drawdown_loss = abs(metrics["max_drawdown"])
        if drawdown_loss - tolerance > constraints.max_drawdown:
            raise ConstraintViolation("portfolio drawdown exceeds max_drawdown")

    if (
        constraints.min_dividend_yield is not None
        and metrics["dividend_yield"] + tolerance < constraints.min_dividend_yield
    ):
        raise ConstraintViolation("portfolio dividend yield is below min_dividend_yield")


def validate_all_constraints(
    weights: dict[str, float],
    metrics: dict[str, float],
    constraints: Constraints,
) -> None:
    validate_weight_constraints(weights, constraints)
    validate_metric_constraints(metrics, constraints)

