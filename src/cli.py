"""CLI entry point for the Lynch-style stock picker."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from data.stub_provider import StubProvider
from data.yahoo_provider import YahooFinanceProvider
from lynch.screener import screen_fundamentals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Peter Lynch-inspired stock screen tools.",
    )
    subparsers = parser.add_subparsers(dest="command")

    screen_parser = subparsers.add_parser("screen", help="Run a Yahoo Finance screen")
    screen_parser.add_argument("tickers", nargs="+", help="Ticker symbols (e.g., AAPL MSFT)")
    screen_parser.add_argument(
        "--risk",
        default="balanced",
        choices=["conservative", "balanced", "aggressive"],
        help="Risk tolerance profile",
    )
    screen_parser.add_argument(
        "--json",
        action="store_true",
        help="Output the full report as JSON",
    )

    render_parser = subparsers.add_parser("render-ui", help="Render a static UI demo bundle")
    render_parser.add_argument("--provider", default="stub", choices=["stub"], help="Data provider")
    render_parser.add_argument("--out", default="dist", help="Output directory")

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


def run_screen(args: argparse.Namespace) -> int:
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


def render_ui(args: argparse.Namespace) -> int:
    if args.provider != "stub":
        raise ValueError("Only the stub provider is supported for render-ui")

    provider = StubProvider()
    fundamentals = [provider.get_fundamentals(ticker) for ticker in provider.list_universe()]
    results = screen_fundamentals(fundamentals, "balanced")
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

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    static_out = out_dir / "static"
    static_out.mkdir(exist_ok=True)

    templates_dir = Path(__file__).resolve().parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("index.html")
    html = template.render(
        results=payload,
        results_json=json.dumps(payload),
        static_prefix="static",
    )

    (out_dir / "index.html").write_text(html)

    static_src = Path(__file__).resolve().parent / "static"
    shutil.copytree(static_src, static_out, dirs_exist_ok=True)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "render-ui":
        return render_ui(args)

    if args.command in (None, "screen"):
        if args.command is None:
            args = parser.parse_args(["screen", *sys.argv[1:]])
        return run_screen(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
