"""Service for fetching earnings data from Yahoo Finance."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd


class EarningsData:
    """Container for earnings data from yfinance."""

    def __init__(
        self,
        period: str,
        period_end_date: Optional[datetime],
        eps: Optional[Decimal],
        revenue: Optional[Decimal],
        ebitda: Optional[Decimal],
        fcf: Optional[Decimal],
    ):
        self.period = period
        self.period_end_date = period_end_date
        self.eps = eps
        self.revenue = revenue
        self.ebitda = ebitda
        self.fcf = fcf


def fetch_earnings_from_yfinance(
    ticker: str,
    num_quarters: int = 5,
    num_years: int = 3,
) -> Dict[str, List[EarningsData]]:
    """
    Fetch earnings data from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol
        num_quarters: Number of recent quarters to fetch
        num_years: Number of recent annual periods to fetch

    Returns:
        Dictionary with 'quarterly' and 'annual' keys, each containing list of EarningsData
    """
    try:
        ticker_obj = yf.Ticker(ticker)

        # Fetch quarterly data
        quarterly_income = ticker_obj.get_income_stmt(freq="quarterly")
        quarterly_cashflow = ticker_obj.get_cash_flow(freq="quarterly")

        # Fetch annual data
        annual_income = ticker_obj.get_income_stmt(freq="yearly")
        annual_cashflow = ticker_obj.get_cash_flow(freq="yearly")

        # Process quarterly data
        quarterly_data = _process_financials(
            quarterly_income,
            quarterly_cashflow,
            num_quarters,
            "quarterly",
        )

        # Process annual data
        annual_data = _process_financials(
            annual_income,
            annual_cashflow,
            num_years,
            "annual",
        )

        return {
            "quarterly": quarterly_data,
            "annual": annual_data,
        }

    except Exception as e:
        # Return empty data on error
        return {
            "quarterly": [],
            "annual": [],
        }


def _process_financials(
    income_stmt: pd.DataFrame,
    cash_flow: pd.DataFrame,
    num_periods: int,
    freq: str,
) -> List[EarningsData]:
    """
    Process income statement and cash flow data into EarningsData objects.

    Args:
        income_stmt: Income statement DataFrame from yfinance
        cash_flow: Cash flow DataFrame from yfinance
        num_periods: Number of periods to extract
        freq: 'quarterly' or 'annual'

    Returns:
        List of EarningsData objects
    """
    results = []

    # Get column names (periods) - they're in reverse chronological order
    if income_stmt.empty:
        return results

    periods = income_stmt.columns[:num_periods]

    for period_date in periods:
        # Extract period end date
        period_end = period_date if isinstance(period_date, datetime) else None

        # Format period string
        if period_end:
            if freq == "quarterly":
                # Format as "2024-Q4"
                quarter = (period_end.month - 1) // 3 + 1
                period_str = f"{period_end.year}-Q{quarter}"
            else:
                # Format as "2024"
                period_str = str(period_end.year)
        else:
            period_str = str(period_date)

        # Extract EPS
        eps = None
        if "DilutedEPS" in income_stmt.index:
            eps_value = income_stmt.loc["DilutedEPS", period_date]
            if pd.notna(eps_value):
                eps = Decimal(str(eps_value))

        # Extract Revenue
        revenue = None
        if "TotalRevenue" in income_stmt.index:
            rev_value = income_stmt.loc["TotalRevenue", period_date]
            if pd.notna(rev_value):
                revenue = Decimal(str(rev_value))

        # Extract EBITDA
        ebitda = None
        if "EBITDA" in income_stmt.index:
            ebitda_value = income_stmt.loc["EBITDA", period_date]
            if pd.notna(ebitda_value):
                ebitda = Decimal(str(ebitda_value))

        # Extract Free Cash Flow
        fcf = None
        if not cash_flow.empty and "FreeCashFlow" in cash_flow.index:
            if period_date in cash_flow.columns:
                fcf_value = cash_flow.loc["FreeCashFlow", period_date]
                if pd.notna(fcf_value):
                    fcf = Decimal(str(fcf_value))

        results.append(
            EarningsData(
                period=period_str,
                period_end_date=period_end,
                eps=eps,
                revenue=revenue,
                ebitda=ebitda,
                fcf=fcf,
            )
        )

    return results
