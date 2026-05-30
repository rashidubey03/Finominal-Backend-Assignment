from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DATA_FILE = Path("Docs/Data.xlsx")


class DataLoadError(ValueError):
    """Raised when source workbook data is missing or malformed."""


@dataclass(frozen=True)
class PortfolioData:
    fund_info: pd.DataFrame
    fund_returns: pd.DataFrame
    factor_returns: pd.DataFrame

    @property
    def tickers(self) -> list[str]:
        return sorted(self.fund_info["ticker"].unique().tolist())

    @property
    def factors(self) -> list[str]:
        return sorted(self.factor_returns["factor"].unique().tolist())

    def fund_metadata(self) -> dict[str, dict[str, float | str | None]]:
        rows = self.fund_info.set_index("ticker").to_dict("index")
        return {
            ticker: {
                "fund_name": row["fund_name"],
                "dividend_yield": None
                if pd.isna(row["dividend_yield"])
                else float(row["dividend_yield"]),
            }
            for ticker, row in rows.items()
        }

    def fund_return_matrix(self, tickers: list[str]) -> pd.DataFrame:
        normalized = normalize_tickers(tickers)
        validate_known_values(normalized, self.tickers, "ticker")
        matrix = self.fund_returns.pivot(
            index="date", columns="ticker", values="total_return"
        )
        return matrix[normalized].dropna().sort_index()

    def factor_return_matrix(self, factors: list[str] | None = None) -> pd.DataFrame:
        matrix = self.factor_returns.pivot(
            index="date", columns="factor", values="total_return"
        )
        if factors is None:
            selected = self.factors
        else:
            selected = [normalize_factor_name(factor) for factor in factors]
            validate_known_values(selected, self.factors, "factor")
        return matrix[selected].dropna().sort_index()


def load_portfolio_data(path: Path = DATA_FILE) -> PortfolioData:
    if not path.exists():
        raise DataLoadError(f"Data file not found: {path}")

    workbook = pd.ExcelFile(path)
    require_sheets(workbook.sheet_names)

    fund_info = normalize_fund_info(pd.read_excel(path, sheet_name="Fund Info"))
    fund_returns = normalize_fund_returns(
        pd.read_excel(path, sheet_name="Fund Returns")
    )
    factor_returns = normalize_factor_returns(
        pd.read_excel(path, sheet_name="Factor Returns")
    )

    return PortfolioData(
        fund_info=fund_info,
        fund_returns=fund_returns,
        factor_returns=factor_returns,
    )


def require_sheets(sheet_names: list[str]) -> None:
    required = {"Fund Info", "Fund Returns", "Factor Returns"}
    missing = required.difference(sheet_names)
    if missing:
        raise DataLoadError(f"Missing sheets: {', '.join(sorted(missing))}")


def require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required.difference(df.columns)
    if missing:
        raise DataLoadError(f"{label} missing columns: {', '.join(sorted(missing))}")


def normalize_fund_info(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, {"ticker", "fund_name", "dividend_yield"}, "Fund Info")
    normalized = df.copy()
    normalized["ticker"] = normalized["ticker"].astype(str).str.upper().str.strip()
    normalized["fund_name"] = normalized["fund_name"].astype(str).str.strip()
    normalized["dividend_yield"] = pd.to_numeric(
        normalized["dividend_yield"], errors="coerce"
    )
    normalized = normalized.dropna(subset=["ticker", "fund_name"])
    return normalized.drop_duplicates("ticker").sort_values("ticker").reset_index(
        drop=True
    )


def normalize_fund_returns(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, {"date", "total_return", "ticker"}, "Fund Returns")
    normalized = df.copy()
    normalized["date"] = pd.to_datetime(normalized["date"])
    normalized["ticker"] = normalized["ticker"].astype(str).str.upper().str.strip()
    normalized["total_return"] = pd.to_numeric(
        normalized["total_return"], errors="coerce"
    )
    normalized = normalized.dropna(subset=["date", "ticker", "total_return"])
    return normalized.sort_values(["date", "ticker"]).reset_index(drop=True)


def normalize_factor_returns(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, {"date", "total_return", "index_ticker"}, "Factor Returns")
    normalized = df.copy()
    normalized["date"] = pd.to_datetime(normalized["date"])
    normalized["factor"] = normalized["index_ticker"].map(normalize_factor_name)
    normalized["total_return"] = pd.to_numeric(
        normalized["total_return"], errors="coerce"
    )
    normalized = normalized.dropna(subset=["date", "factor", "total_return"])
    return normalized[["date", "factor", "total_return"]].sort_values(
        ["date", "factor"]
    ).reset_index(drop=True)


def normalize_tickers(tickers: list[str]) -> list[str]:
    return [ticker.upper().strip() for ticker in tickers]


def normalize_factor_name(name: str) -> str:
    return str(name).upper().replace(" FACTOR", "").strip().lower()


def validate_known_values(values: list[str], known: list[str], label: str) -> None:
    missing = sorted(set(values).difference(known))
    if missing:
        raise DataLoadError(f"Unknown {label}s: {', '.join(missing)}")

