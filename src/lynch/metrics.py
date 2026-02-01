"""Metric calculations inspired by Peter Lynch's principles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LynchMetrics:
    pe_ratio: Optional[float]
    earnings_growth_pct: Optional[float]
    revenue_growth_pct: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]

    @property
    def peg_ratio(self) -> Optional[float]:
        return compute_peg_ratio(self.pe_ratio, self.earnings_growth_pct)


def compute_peg_ratio(pe_ratio: Optional[float], growth_pct: Optional[float]) -> Optional[float]:
    """Return the PEG ratio using a percent growth rate.

    PEG = P/E divided by earnings growth rate (%). Lower is generally better.
    """
    if pe_ratio is None or growth_pct is None:
        return None
    if pe_ratio <= 0 or growth_pct <= 0:
        return None
    return pe_ratio / growth_pct


def compute_debt_to_equity(total_debt: Optional[float], total_equity: Optional[float]) -> Optional[float]:
    if total_debt is None or total_equity in (None, 0):
        return None
    return total_debt / total_equity


def compute_current_ratio(current_assets: Optional[float], current_liabilities: Optional[float]) -> Optional[float]:
    if current_assets is None or current_liabilities in (None, 0):
        return None
    return current_assets / current_liabilities


def prefer_growth_rate(
    earnings_growth_pct: Optional[float],
    revenue_growth_pct: Optional[float],
) -> Optional[float]:
    """Prefer earnings growth, fall back to revenue growth."""
    return earnings_growth_pct if earnings_growth_pct is not None else revenue_growth_pct
