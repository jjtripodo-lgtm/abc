"""FastAPI app exposing the Lynch screener UI and API."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from data.provider import DataProvider
from data.stub_provider import StubProvider
from lynch.screener import screen_fundamentals


class HealthResponse(BaseModel):
    status: str


class ScreenRequest(BaseModel):
    tickers: list[str] = []
    risk_tolerance: str = "balanced"
    universe: str = "stub"


class ReasonPayload(BaseModel):
    level: str
    code: str
    message: str
    value: float | None = None
    threshold: float | None = None


class ScreenResultPayload(BaseModel):
    ticker: str
    name: str
    score: int
    rating: str
    category: str
    metrics: dict[str, float | None]
    reasons: list[ReasonPayload]


class ScreenResponse(BaseModel):
    results: list[ScreenResultPayload]


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Lynch Screener")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _build_payload(results: list) -> list[ScreenResultPayload]:
    return [
        ScreenResultPayload(
            ticker=result.ticker,
            name=result.name,
            score=result.score,
            rating=result.rating,
            category=result.category,
            metrics=result.metrics,
            reasons=[ReasonPayload(**asdict(reason)) for reason in result.reasons],
        )
        for result in results
    ]


@app.get("/", response_class=HTMLResponse)
def index(request: Request, demo: bool = False) -> HTMLResponse:
    results_payload: list[ScreenResultPayload] = []
    if demo:
        provider = StubProvider()
        fundamentals = [provider.get_fundamentals(ticker) for ticker in provider.list_universe()]
        results = screen_fundamentals(fundamentals, "balanced")
        results_payload = _build_payload(results)

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": results_payload,
            "results_json": json.dumps([payload.model_dump() for payload in results_payload]),
            "static_prefix": "/static",
        },
    )

app = FastAPI(title="Lynch Screener")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/hello")
def hello() -> dict[str, str]:
    return {"message": "hello screener"}


@app.post("/api/screen", response_model=ScreenResponse)
def screen(request: ScreenRequest) -> ScreenResponse:
    provider = _resolve_provider(request.universe)
    tickers = request.tickers or list(provider.list_universe())

    try:
        fundamentals = [provider.get_fundamentals(ticker) for ticker in tickers]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=503, detail=f"Provider failure: {exc}") from exc

    results = screen_fundamentals(fundamentals, request.risk_tolerance)
    payload = [
        ScreenResultPayload(
            ticker=result.ticker,
            name=result.name,
            score=result.score,
            rating=result.rating,
            category=result.category,
            metrics=result.metrics,
            reasons=[ReasonPayload(**asdict(reason)) for reason in result.reasons],
        )
        for result in results
    ]

    return ScreenResponse(results=payload)


def _resolve_provider(universe: str) -> DataProvider:
    if universe == "stub":
        return StubProvider()
    raise HTTPException(status_code=400, detail=f"Unknown universe: {universe}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
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
