"""Shared data models for the screener."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Fundamentals:
    ticker: str
    name: str
    price: Optional[float]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    revenue_cagr_5y: Optional[float]
    eps_growth_5y: Optional[float]
    operating_margin: Optional[float]
    fcf_margin: Optional[float]
    roe: Optional[float]
    debt_to_equity: Optional[float]
    net_debt_to_ebitda: Optional[float]
    interest_coverage: Optional[float]
    current_ratio: Optional[float]
    shares_outstanding: Optional[float]
    free_cash_flow: Optional[float]


@dataclass(frozen=True)
class ReasonCode:
    level: str  # positive | warning | negative
    code: str
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None


@dataclass(frozen=True)
class ScreenResult:
    ticker: str
    name: str
    score: int
    rating: str
    category: str
    metrics: dict[str, Optional[float]]
    reasons: tuple[ReasonCode, ...]
