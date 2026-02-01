"""Data provider interface and mock implementation for financial data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol


@dataclass(frozen=True)
class IncomeStatement:
    period_end: date
    revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    earnings_per_share: float
    dividends_per_share: float


@dataclass(frozen=True)
class BalanceSheet:
    period_end: date
    total_assets: float
    total_liabilities: float
    shareholder_equity: float
    total_debt: float
    cash_and_equivalents: float


@dataclass(frozen=True)
class CashFlowStatement:
    period_end: date
    operating_cash_flow: float
    capital_expenditures: float
    free_cash_flow: float


@dataclass(frozen=True)
class FinancialStatements:
    income_statements: Iterable[IncomeStatement]
    balance_sheets: Iterable[BalanceSheet]
    cash_flow_statements: Iterable[CashFlowStatement]


@dataclass(frozen=True)
class GrowthRates:
    revenue_cagr: float
    eps_cagr: float
    free_cash_flow_cagr: float


@dataclass(frozen=True)
class PriceData:
    as_of: date
    price: float
    shares_outstanding: float


class DataProvider(Protocol):
    """Interface for loading financial data used for Lynch metrics."""

    def get_financial_statements(self, ticker: str) -> FinancialStatements:
        """Return historical financial statements for a ticker."""

    def get_growth_rates(self, ticker: str) -> GrowthRates:
        """Return growth rates for a ticker."""

    def get_price_data(self, ticker: str) -> PriceData:
        """Return latest price data for a ticker."""


class MockDataProvider:
    """Stub provider that returns deterministic example data."""

    def get_financial_statements(self, ticker: str) -> FinancialStatements:
        del ticker
        income = [
            IncomeStatement(
                period_end=date(2023, 12, 31),
                revenue=150_000_000.0,
                gross_profit=75_000_000.0,
                operating_income=30_000_000.0,
                net_income=22_000_000.0,
                earnings_per_share=2.25,
                dividends_per_share=0.4,
            )
        ]
        balance = [
            BalanceSheet(
                period_end=date(2023, 12, 31),
                total_assets=220_000_000.0,
                total_liabilities=120_000_000.0,
                shareholder_equity=100_000_000.0,
                total_debt=45_000_000.0,
                cash_and_equivalents=18_000_000.0,
            )
        ]
        cash_flow = [
            CashFlowStatement(
                period_end=date(2023, 12, 31),
                operating_cash_flow=28_000_000.0,
                capital_expenditures=-6_000_000.0,
                free_cash_flow=22_000_000.0,
            )
        ]
        return FinancialStatements(
            income_statements=income,
            balance_sheets=balance,
            cash_flow_statements=cash_flow,
        )

    def get_growth_rates(self, ticker: str) -> GrowthRates:
        del ticker
        return GrowthRates(
            revenue_cagr=0.12,
            eps_cagr=0.15,
            free_cash_flow_cagr=0.1,
        )

    def get_price_data(self, ticker: str) -> PriceData:
        del ticker
        return PriceData(
            as_of=date(2024, 1, 2),
            price=42.5,
            shares_outstanding=50_000_000.0,
        )
