"""Provider interface for fetching fundamentals."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from models import Fundamentals


class DataProvider(ABC):
    @abstractmethod
    def get_fundamentals(self, ticker: str) -> Fundamentals:
        raise NotImplementedError

    @abstractmethod
    def list_universe(self) -> Iterable[str]:
        raise NotImplementedError
