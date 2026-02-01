"""Scoring utilities for a Lynch-style stock screen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .metrics import LynchMetrics, prefer_growth_rate


@dataclass(frozen=True)
class ScoreResult:
    score: int
    rating: str
    notes: tuple[str, ...]


def score_stock(metrics: LynchMetrics) -> ScoreResult:
    """Score a stock using a simplified Peter Lynch-inspired rubric.

    The rubric favors reasonable valuations relative to growth, low debt, and
    decent liquidity. Returns a score from 0-10 and a rating label.
    """
    score = 0
    notes: list[str] = []

    peg = metrics.peg_ratio
    growth = prefer_growth_rate(metrics.earnings_growth_pct, metrics.revenue_growth_pct)

    if peg is None:
        notes.append("PEG unavailable or invalid")
    elif peg <= 1:
        score += 3
        notes.append("PEG <= 1 (attractive valuation vs growth)")
    elif peg <= 1.5:
        score += 2
        notes.append("PEG between 1 and 1.5")
    elif peg <= 2:
        score += 1
        notes.append("PEG between 1.5 and 2")
    else:
        notes.append("PEG above 2")

    if growth is None:
        notes.append("Growth unavailable")
    elif growth >= 15:
        score += 3
        notes.append("Growth >= 15%")
    elif growth >= 8:
        score += 2
        notes.append("Growth between 8% and 15%")
    elif growth >= 4:
        score += 1
        notes.append("Growth between 4% and 8%")
    else:
        notes.append("Low growth")

    if metrics.debt_to_equity is None:
        notes.append("Debt-to-equity unavailable")
    elif metrics.debt_to_equity <= 0.5:
        score += 2
        notes.append("Low leverage (D/E <= 0.5)")
    elif metrics.debt_to_equity <= 1:
        score += 1
        notes.append("Moderate leverage (D/E <= 1)")
    else:
        notes.append("High leverage")

    if metrics.current_ratio is None:
        notes.append("Current ratio unavailable")
    elif metrics.current_ratio >= 1.5:
        score += 2
        notes.append("Healthy current ratio")
    elif metrics.current_ratio >= 1:
        score += 1
        notes.append("Adequate current ratio")
    else:
        notes.append("Weak current ratio")

    rating = _rating_for_score(score)
    return ScoreResult(score=score, rating=rating, notes=tuple(notes))


def _rating_for_score(score: int) -> str:
    if score >= 8:
        return "Strong"
    if score >= 5:
        return "Watch"
    return "Caution"
