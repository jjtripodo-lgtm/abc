# v1 Product Requirements Document (PRD)

## Goal
Build a Lynch-inspired stock screener and ranker that ingests fundamentals, applies
hard filters, calculates a transparent score, and returns a ranked list with
reason codes.

## Inputs
- **Tickers**: manual list or a provider-backed universe (v1 uses a stub universe).
- **Risk tolerance**: conservative / balanced / aggressive (adjusts thresholds).
- **Optional filters** (v1 UI only): exclude sectors, min market cap, min liquidity.

## Outputs (per ticker)
- **Overall score (0–100)**
- **Category label**: stalwart / fast grower / slow grower / turnaround / asset play
- **Key metrics**: P/E, PEG, debt ratios, margins, ROE, FCF, growth rates
- **Reason codes**: positive / warning / negative flags with explanations

## User Flows
1. User opens the web page.
2. User enters tickers or selects the stub universe.
3. User chooses risk tolerance and runs the screen.
4. App returns ranked results with metrics and reason codes.

## Acceptance Criteria
- One command runs the app; user can open a page and run a screen.
- At least 10 tickers are ranked using stub fundamentals.
- Each ticker includes score, category, metrics, and reason codes.
- Provider is swappable (interface in place + stub implementation).
- Tests cover scoring, endpoint integration, and UI snapshot.

## Non-goals (v1)
- Intraday pricing or portfolio optimization.
- Long-horizon backtesting.
- Any promise of guaranteed picks.
