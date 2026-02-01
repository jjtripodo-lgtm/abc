"""CLI entry point for the Lynch-style stock picker."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from data.yahoo_provider import YahooFinanceProvider
from lynch.screener import screen_fundamentals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Peter Lynch-inspired stock screen using Yahoo Finance data.",
    )
    parser.add_argument("tickers", nargs="+", help="Ticker symbols (e.g., AAPL MSFT)")
    parser.add_argument(
        "--risk",
        default="balanced",
        choices=["conservative", "balanced", "aggressive"],
        help="Risk tolerance profile",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the full report as JSON",
    )
    return parser


def format_report(result: dict) -> str:
    lines = [f"Ticker: {result['ticker']} ({result['name']})"]
    lines.append(f"Score: {result['score']} ({result['rating']})")
    lines.append(f"Category: {result['category']}")
    lines.append("Metrics:")
    for key, value in result["metrics"].items():
        lines.append(f"  {key}: {value}")
    lines.append("Reasons:")
    for reason in result["reasons"]:
        lines.append(f"  - {reason['message']}")
    return "\n".join(lines)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    provider = YahooFinanceProvider()
    fundamentals = [provider.get_fundamentals(ticker) for ticker in args.tickers]
    results = screen_fundamentals(fundamentals, args.risk)

    payload = [
        {
            "ticker": result.ticker,
            "name": result.name,
            "score": result.score,
            "rating": result.rating,
            "category": result.category,
            "metrics": result.metrics,
            "reasons": [asdict(reason) for reason in result.reasons],
        }
        for result in results
    ]

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for item in payload:
            print(format_report(item))
            print("-")

    return 0


if __name__ == "__main__":
    sys.exit(main())
