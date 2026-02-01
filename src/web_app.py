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


class ScreenRequest(BaseModel):
    tickers: list[str] = []
    risk_tolerance: str = "balanced"
    universe: str = "stub"


class ScreenResponse(BaseModel):
    results: list[dict[str, Any]]


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Lynch Screener")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


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

    results = screen_fundamentals(fundamentals, request.risk_tolerance)
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

    return ScreenResponse(results=payload)


def _resolve_provider(universe: str) -> DataProvider:
    if universe == "stub":
        return StubProvider()
    raise HTTPException(status_code=400, detail=f"Unknown universe: {universe}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.web_app:app", host="0.0.0.0", port=8000, reload=True)
