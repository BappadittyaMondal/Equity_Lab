"""Data ingestion framework for IERL Research Database.

Provides ingesters that pull real financial data from external sources
and store it in the append-only, point-in-time ResearchDataStore.
"""

from .financial_ingester import FinancialIngester
from .daily_price_ingester import DailyPriceIngester

__all__ = ["FinancialIngester", "DailyPriceIngester"]
