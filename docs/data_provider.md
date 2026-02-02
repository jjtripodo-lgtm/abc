# Data provider integration guide

## Overview
The `DataProvider` protocol in `src/data/provider.py` defines the minimal contract required to
fetch financial statements, growth rates, and price data. Implementations can wrap APIs such as
SEC filings, commercial market data vendors, or internal data warehouses.

The `MockDataProvider` class is a stub implementation that returns deterministic sample data. It
is useful for development, tests, and examples while real data sources are wired up.

## Required fields for Lynch metrics
The Lynch (Peter Lynch) metrics commonly rely on the following inputs. The interface structures
these as required fields to keep calculations consistent across data sources:

### Income statement (`IncomeStatement`)
- `revenue`
- `net_income`
- `earnings_per_share` (EPS)
- `dividends_per_share`
- `gross_profit`
- `operating_income`

### Balance sheet (`BalanceSheet`)
- `shareholder_equity`
- `total_debt`
- `total_assets`
- `total_liabilities`
- `cash_and_equivalents`

### Cash flow (`CashFlowStatement`)
- `operating_cash_flow`
- `capital_expenditures`
- `free_cash_flow`

### Growth rates (`GrowthRates`)
- `revenue_cagr`
- `eps_cagr`
- `free_cash_flow_cagr`

### Price data (`PriceData`)
- `price`
- `shares_outstanding`
- `as_of`

## Plugging in a real data source
1. **Create a new provider class**
   - Implement the three methods in `DataProvider`:
     - `get_financial_statements(ticker)`
     - `get_growth_rates(ticker)`
     - `get_price_data(ticker)`

2. **Map raw fields to the required schema**
   - Normalize vendor-specific field names to the dataclasses in `src/data/provider.py`.
   - Convert all monetary values to floats and use consistent currency units.
   - Populate `period_end` with a `datetime.date` for each reporting period.

3. **Handle missing data explicitly**
   - If a vendor is missing a required field, decide on a fallback strategy:
     - Fetch the field from another source, or
     - Raise a clear error early so downstream Lynch metric calculations can be skipped.

4. **Document data provenance**
   - Capture the vendor name, API version, and retrieval time in logs or metadata so that
     outputs can be audited.

## Example skeleton
```python
from src.data.provider import (
    BalanceSheet,
    CashFlowStatement,
    DataProvider,
    FinancialStatements,
    GrowthRates,
    IncomeStatement,
    PriceData,
)

class VendorDataProvider:
    def __init__(self, client: "VendorClient") -> None:
        self._client = client

    def get_financial_statements(self, ticker: str) -> FinancialStatements:
        raw = self._client.fetch_financials(ticker)
        # Map vendor fields to the dataclasses.
        return FinancialStatements(
            income_statements=[
                IncomeStatement(
                    period_end=raw["period_end"],
                    revenue=raw["revenue"],
                    gross_profit=raw["gross_profit"],
                    operating_income=raw["operating_income"],
                    net_income=raw["net_income"],
                    earnings_per_share=raw["eps"],
                    dividends_per_share=raw["dividends_per_share"],
                )
            ],
            balance_sheets=[
                BalanceSheet(
                    period_end=raw["period_end"],
                    total_assets=raw["total_assets"],
                    total_liabilities=raw["total_liabilities"],
                    shareholder_equity=raw["shareholder_equity"],
                    total_debt=raw["total_debt"],
                    cash_and_equivalents=raw["cash_and_equivalents"],
                )
            ],
            cash_flow_statements=[
                CashFlowStatement(
                    period_end=raw["period_end"],
                    operating_cash_flow=raw["operating_cash_flow"],
                    capital_expenditures=raw["capital_expenditures"],
                    free_cash_flow=raw["free_cash_flow"],
                )
            ],
        )

    def get_growth_rates(self, ticker: str) -> GrowthRates:
        growth = self._client.fetch_growth(ticker)
        return GrowthRates(
            revenue_cagr=growth["revenue_cagr"],
            eps_cagr=growth["eps_cagr"],
            free_cash_flow_cagr=growth["free_cash_flow_cagr"],
        )

    def get_price_data(self, ticker: str) -> PriceData:
        price = self._client.fetch_price(ticker)
        return PriceData(
            as_of=price["as_of"],
            price=price["price"],
            shares_outstanding=price["shares_outstanding"],
        )
```
