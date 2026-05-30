ACCEPTANCE_CASES = [
    {
        "name": "case_1_equal_weight_sanity",
        "payload": {
            "holdings": [
                {"ticker": "IEFA", "weight": 25},
                {"ticker": "SPY", "weight": 75},
            ],
            "strategy": "equal_weights",
        },
        "requires_factor_betas": False,
    },
    {
        "name": "case_2_risk_parity",
        "payload": {
            "holdings": [
                {"ticker": "VEA", "weight": 25},
                {"ticker": "AGG", "weight": 75},
            ],
            "strategy": "risk_parity",
        },
        "requires_factor_betas": False,
    },
    {
        "name": "case_3_minimize_volatility",
        "payload": {
            "holdings": [
                {"ticker": "SPY", "weight": 60},
                {"ticker": "AGG", "weight": 30},
                {"ticker": "GLD", "weight": 10},
            ],
            "strategy": "minimize_volatility",
        },
        "requires_factor_betas": False,
    },
    {
        "name": "case_4_maximize_sharpe",
        "payload": {
            "holdings": [
                {"ticker": "IEFA", "weight": 20},
                {"ticker": "GLD", "weight": 20},
                {"ticker": "AGG", "weight": 20},
                {"ticker": "VEA", "weight": 20},
                {"ticker": "SPY", "weight": 20},
            ],
            "strategy": "maximize_sharpe",
        },
        "requires_factor_betas": False,
    },
    {
        "name": "case_5_constrained_sharpe",
        "payload": {
            "holdings": [
                {"ticker": "IEFA", "weight": 20},
                {"ticker": "GLD", "weight": 20},
                {"ticker": "AGG", "weight": 20},
                {"ticker": "VEA", "weight": 20},
                {"ticker": "SPY", "weight": 20},
            ],
            "strategy": "maximize_sharpe",
            "constraints": {
                "min_dividend_yield": 0.025,
                "min_weight": 5,
                "max_weight": 40,
            },
        },
        "requires_factor_betas": False,
    },
    {
        "name": "case_6_momentum_factor_bonus",
        "payload": {
            "holdings": [
                {"ticker": "IEFA", "weight": 20},
                {"ticker": "GLD", "weight": 20},
                {"ticker": "AGG", "weight": 20},
                {"ticker": "VEA", "weight": 20},
                {"ticker": "SPY", "weight": 20},
            ],
            "strategy": "optimize_factor_exposure",
            "factor_target": "momentum",
        },
        "requires_factor_betas": True,
    },
]

