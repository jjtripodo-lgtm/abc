"""Yahoo Finance data provider."""

from __future__ import annotations

from typing import Iterable, Optional

import yfinance as yf

from data.provider import DataProvider
from models import Fundamentals


class YahooFinanceProvider(DataProvider):
    def get_fundamentals(self, ticker: str) -> Fundamentals:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.get_info()

        return Fundamentals(
            ticker=ticker.upper(),
            name=info.get("shortName", ticker.upper()),
            price=_safe_float(info.get("currentPrice")),
            market_cap=_safe_float(info.get("marketCap")),
            pe_ratio=_safe_float(info.get("trailingPE")),
            revenue_cagr_5y=_safe_percent(info.get("revenueGrowth")),
            eps_growth_5y=_safe_percent(info.get("earningsGrowth")),
            operating_margin=_safe_percent(info.get("operatingMargins")),
            fcf_margin=_safe_percent(info.get("freeCashflow")),
            roe=_safe_percent(info.get("returnOnEquity")),
            debt_to_equity=_safe_float(info.get("debtToEquity")),
            net_debt_to_ebitda=_safe_float(info.get("netDebtToEBITDA")),
            interest_coverage=_safe_float(info.get("interestCoverage")),
            current_ratio=_safe_float(info.get("currentRatio")),
            shares_outstanding=_safe_float(info.get("sharesOutstanding")),
            free_cash_flow=_safe_float(info.get("freeCashflow")),
        )

    def list_universe(self) -> Iterable[str]:
        raise NotImplementedError("Yahoo Finance provider does not define a universe")


def _safe_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_percent(value: object) -> Optional[float]:
    try:
        return float(value) * 100
    except (TypeError, ValueError):
        return None
