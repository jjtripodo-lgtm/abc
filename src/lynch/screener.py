"""Lynch-inspired screening and scoring logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from models import Fundamentals, ReasonCode, ScreenResult


@dataclass(frozen=True)
class RiskProfile:
    name: str
    max_debt_to_equity: float
    min_interest_coverage: float
    min_current_ratio: float
    min_fcf_margin: float
    growth_floor: float


PROFILES: dict[str, RiskProfile] = {
    "conservative": RiskProfile(
        name="conservative",
        max_debt_to_equity=1.0,
        min_interest_coverage=4.0,
        min_current_ratio=1.2,
        min_fcf_margin=2.0,
        growth_floor=6.0,
    ),
    "balanced": RiskProfile(
        name="balanced",
        max_debt_to_equity=1.5,
        min_interest_coverage=3.0,
        min_current_ratio=1.0,
        min_fcf_margin=1.0,
        growth_floor=4.0,
    ),
    "aggressive": RiskProfile(
        name="aggressive",
        max_debt_to_equity=2.0,
        min_interest_coverage=2.0,
        min_current_ratio=0.8,
        min_fcf_margin=0.0,
        growth_floor=2.0,
    ),
}


def screen_fundamentals(
    fundamentals: Iterable[Fundamentals],
    risk_tolerance: str = "balanced",
) -> list[ScreenResult]:
    profile = PROFILES.get(risk_tolerance, PROFILES["balanced"])

    results = [
        _score_one(item, profile)
        for item in fundamentals
    ]

    return sorted(results, key=lambda item: item.score, reverse=True)


def _score_one(fundamentals: Fundamentals, profile: RiskProfile) -> ScreenResult:
    reasons: list[ReasonCode] = []

    missing_fields = _missing_fields(fundamentals)
    if missing_fields:
        reasons.append(
            ReasonCode(
                level="negative",
                code="MISSING_DATA",
                message=f"Missing required data: {', '.join(missing_fields)}",
            )
        )

    hard_fail = bool(missing_fields)

    if _float_value(fundamentals.debt_to_equity) is not None and fundamentals.debt_to_equity > profile.max_debt_to_equity:
        reasons.append(
            ReasonCode(
                level="negative",
                code="DEBT_HIGH",
                message=f"Debt/Equity {fundamentals.debt_to_equity:.2f} exceeds {profile.max_debt_to_equity:.2f}",
            )
        )
        hard_fail = True

    if _float_value(fundamentals.interest_coverage) is not None and fundamentals.interest_coverage < profile.min_interest_coverage:
        reasons.append(
            ReasonCode(
                level="negative",
                code="INTEREST_COVERAGE_LOW",
                message=f"Interest coverage {fundamentals.interest_coverage:.1f} below {profile.min_interest_coverage:.1f}x",
            )
        )
        hard_fail = True

    if _float_value(fundamentals.current_ratio) is not None and fundamentals.current_ratio < profile.min_current_ratio:
        reasons.append(
            ReasonCode(
                level="warning",
                code="CURRENT_RATIO_LOW",
                message=f"Current ratio {fundamentals.current_ratio:.2f} below {profile.min_current_ratio:.2f}",
            )
        )

    if _float_value(fundamentals.fcf_margin) is not None and fundamentals.fcf_margin < profile.min_fcf_margin:
        reasons.append(
            ReasonCode(
                level="negative",
                code="FCF_WEAK",
                message=f"FCF margin {fundamentals.fcf_margin:.2f}% below {profile.min_fcf_margin:.2f}%",
            )
        )
        hard_fail = True

    peg = _peg_ratio(fundamentals)
    score_breakdown = {
        "value": _score_value(fundamentals, peg, reasons),
        "growth": _score_growth(fundamentals, profile, reasons),
        "quality": _score_quality(fundamentals, reasons),
        "balance": _score_balance(fundamentals, profile, reasons),
    }

    raw_score = sum(score_breakdown.values())
    score = 0 if hard_fail else int(round(raw_score))
    rating = _rating_for_score(score, hard_fail)
    category = _category_for_fundamentals(fundamentals)

    metrics = {
        "pe_ratio": fundamentals.pe_ratio,
        "peg_ratio": peg,
        "revenue_cagr_5y": fundamentals.revenue_cagr_5y,
        "eps_growth_5y": fundamentals.eps_growth_5y,
        "operating_margin": fundamentals.operating_margin,
        "fcf_margin": fundamentals.fcf_margin,
        "roe": fundamentals.roe,
        "debt_to_equity": fundamentals.debt_to_equity,
        "net_debt_to_ebitda": fundamentals.net_debt_to_ebitda,
        "interest_coverage": fundamentals.interest_coverage,
        "current_ratio": fundamentals.current_ratio,
    }

    return ScreenResult(
        ticker=fundamentals.ticker,
        name=fundamentals.name,
        score=score,
        rating=rating,
        category=category,
        metrics=metrics,
        reasons=tuple(reasons),
    )


def _missing_fields(fundamentals: Fundamentals) -> list[str]:
    required = {
        "pe_ratio": fundamentals.pe_ratio,
        "revenue_cagr_5y": fundamentals.revenue_cagr_5y,
        "eps_growth_5y": fundamentals.eps_growth_5y,
        "debt_to_equity": fundamentals.debt_to_equity,
        "interest_coverage": fundamentals.interest_coverage,
        "current_ratio": fundamentals.current_ratio,
        "fcf_margin": fundamentals.fcf_margin,
    }
    return [name for name, value in required.items() if value is None]


def _score_value(fundamentals: Fundamentals, peg: Optional[float], reasons: list[ReasonCode]) -> float:
    if peg is None:
        reasons.append(
            ReasonCode(level="warning", code="PEG_MISSING", message="PEG ratio unavailable")
        )
        return 0

    if peg <= 1:
        reasons.append(ReasonCode(level="positive", code="PEG_ATTRACTIVE", message=f"PEG {peg:.2f} <= 1"))
        return 30
    if peg <= 1.5:
        reasons.append(ReasonCode(level="positive", code="PEG_FAIR", message=f"PEG {peg:.2f} between 1-1.5"))
        return 24
    if peg <= 2:
        reasons.append(ReasonCode(level="warning", code="PEG_RICH", message=f"PEG {peg:.2f} between 1.5-2"))
        return 16

    reasons.append(ReasonCode(level="negative", code="PEG_EXPENSIVE", message=f"PEG {peg:.2f} above 2"))
    return 8


def _score_growth(fundamentals: Fundamentals, profile: RiskProfile, reasons: list[ReasonCode]) -> float:
    growth = _combined_growth(fundamentals)
    if growth is None:
        reasons.append(ReasonCode(level="warning", code="GROWTH_MISSING", message="Growth metrics missing"))
        return 0

    if growth >= 20:
        reasons.append(ReasonCode(level="positive", code="GROWTH_STRONG", message=f"Growth {growth:.1f}%"))
        return 25
    if growth >= 12:
        reasons.append(ReasonCode(level="positive", code="GROWTH_HEALTHY", message=f"Growth {growth:.1f}%"))
        return 20
    if growth >= 8:
        reasons.append(ReasonCode(level="warning", code="GROWTH_MODERATE", message=f"Growth {growth:.1f}%"))
        return 15
    if growth >= profile.growth_floor:
        reasons.append(ReasonCode(level="warning", code="GROWTH_LOW", message=f"Growth {growth:.1f}%"))
        return 8

    reasons.append(ReasonCode(level="negative", code="GROWTH_WEAK", message=f"Growth {growth:.1f}%"))
    return 2


def _score_quality(fundamentals: Fundamentals, reasons: list[ReasonCode]) -> float:
    scores = []

    if fundamentals.operating_margin is not None:
        if fundamentals.operating_margin >= 20:
            reasons.append(
                ReasonCode(level="positive", code="MARGIN_STRONG", message=f"Operating margin {fundamentals.operating_margin:.1f}%")
            )
            scores.append(10)
        elif fundamentals.operating_margin >= 10:
            reasons.append(
                ReasonCode(level="warning", code="MARGIN_OK", message=f"Operating margin {fundamentals.operating_margin:.1f}%")
            )
            scores.append(7)
        else:
            reasons.append(
                ReasonCode(level="warning", code="MARGIN_THIN", message=f"Operating margin {fundamentals.operating_margin:.1f}%")
            )
            scores.append(4)

    if fundamentals.fcf_margin is not None:
        if fundamentals.fcf_margin >= 15:
            reasons.append(
                ReasonCode(level="positive", code="FCF_STRONG", message=f"FCF margin {fundamentals.fcf_margin:.1f}%")
            )
            scores.append(8)
        elif fundamentals.fcf_margin >= 5:
            reasons.append(
                ReasonCode(level="warning", code="FCF_OK", message=f"FCF margin {fundamentals.fcf_margin:.1f}%")
            )
            scores.append(5)
        else:
            reasons.append(
                ReasonCode(level="warning", code="FCF_THIN", message=f"FCF margin {fundamentals.fcf_margin:.1f}%")
            )
            scores.append(2)

    if fundamentals.roe is not None:
        if fundamentals.roe >= 20:
            reasons.append(
                ReasonCode(level="positive", code="ROE_STRONG", message=f"ROE {fundamentals.roe:.1f}%")
            )
            scores.append(7)
        elif fundamentals.roe >= 10:
            reasons.append(
                ReasonCode(level="warning", code="ROE_OK", message=f"ROE {fundamentals.roe:.1f}%")
            )
            scores.append(5)
        else:
            reasons.append(
                ReasonCode(level="warning", code="ROE_WEAK", message=f"ROE {fundamentals.roe:.1f}%")
            )
            scores.append(2)

    if not scores:
        return 0

    return min(sum(scores), 25)


def _score_balance(fundamentals: Fundamentals, profile: RiskProfile, reasons: list[ReasonCode]) -> float:
    score = 0

    if fundamentals.debt_to_equity is not None:
        if fundamentals.debt_to_equity <= 0.5:
            reasons.append(
                ReasonCode(level="positive", code="DEBT_LIGHT", message=f"Debt/Equity {fundamentals.debt_to_equity:.2f}")
            )
            score += 6
        elif fundamentals.debt_to_equity <= profile.max_debt_to_equity:
            reasons.append(
                ReasonCode(level="warning", code="DEBT_MANAGEABLE", message=f"Debt/Equity {fundamentals.debt_to_equity:.2f}")
            )
            score += 4

    if fundamentals.net_debt_to_ebitda is not None:
        if fundamentals.net_debt_to_ebitda <= 1:
            reasons.append(
                ReasonCode(level="positive", code="NET_DEBT_LOW", message=f"Net debt/EBITDA {fundamentals.net_debt_to_ebitda:.1f}x")
            )
            score += 6
        elif fundamentals.net_debt_to_ebitda <= 3:
            reasons.append(
                ReasonCode(level="warning", code="NET_DEBT_OK", message=f"Net debt/EBITDA {fundamentals.net_debt_to_ebitda:.1f}x")
            )
            score += 4
        else:
            reasons.append(
                ReasonCode(level="negative", code="NET_DEBT_HIGH", message=f"Net debt/EBITDA {fundamentals.net_debt_to_ebitda:.1f}x")
            )

    if fundamentals.interest_coverage is not None:
        if fundamentals.interest_coverage >= 8:
            reasons.append(
                ReasonCode(level="positive", code="COVERAGE_STRONG", message=f"Interest coverage {fundamentals.interest_coverage:.1f}x")
            )
            score += 5
        elif fundamentals.interest_coverage >= profile.min_interest_coverage:
            reasons.append(
                ReasonCode(level="warning", code="COVERAGE_OK", message=f"Interest coverage {fundamentals.interest_coverage:.1f}x")
            )
            score += 3

    if fundamentals.current_ratio is not None:
        if fundamentals.current_ratio >= 1.5:
            reasons.append(
                ReasonCode(level="positive", code="CURRENT_STRONG", message=f"Current ratio {fundamentals.current_ratio:.2f}")
            )
            score += 3
        elif fundamentals.current_ratio >= profile.min_current_ratio:
            reasons.append(
                ReasonCode(level="warning", code="CURRENT_OK", message=f"Current ratio {fundamentals.current_ratio:.2f}")
            )
            score += 2

    return min(score, 20)


def _combined_growth(fundamentals: Fundamentals) -> Optional[float]:
    growth_values = [value for value in [fundamentals.revenue_cagr_5y, fundamentals.eps_growth_5y] if value is not None]
    if not growth_values:
        return None
    return sum(growth_values) / len(growth_values)


def _peg_ratio(fundamentals: Fundamentals) -> Optional[float]:
    growth = _combined_growth(fundamentals)
    if fundamentals.pe_ratio is None or growth is None or growth <= 0:
        return None
    return fundamentals.pe_ratio / growth


def _rating_for_score(score: int, hard_fail: bool) -> str:
    if hard_fail:
        return "Fail"
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Watch"
    return "Caution"


def _category_for_fundamentals(fundamentals: Fundamentals) -> str:
    growth = _combined_growth(fundamentals)

    if growth is None:
        return "unknown"
    if growth >= 15:
        return "fast grower"
    if growth >= 8:
        return "stalwart"
    if growth >= 3:
        return "slow grower"
    if growth < 0:
        return "turnaround"
    if fundamentals.pe_ratio is not None and fundamentals.pe_ratio <= 12:
        return "asset play"
    return "slow grower"


def _float_value(value: Optional[float]) -> Optional[float]:
    return value if value is not None else None
