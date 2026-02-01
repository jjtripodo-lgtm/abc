"""Stub provider with deterministic fundamentals for tests and UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from data.provider import DataProvider
from models import Fundamentals


class StubProvider(DataProvider):
    def __init__(self, data_path: Path | None = None) -> None:
        self._data_path = data_path or Path(__file__).with_name("stub_data.json")
        self._data = _load_data(self._data_path)

    def get_fundamentals(self, ticker: str) -> Fundamentals:
        data = self._data.get(ticker.upper())
        if data is None:
            raise KeyError(f"Ticker not found in stub provider: {ticker}")
        return Fundamentals(**data)

    def list_universe(self) -> Iterable[str]:
        return sorted(self._data.keys())


def _load_data(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text())
    return {item["ticker"].upper(): item for item in raw}
