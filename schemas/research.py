
"""Pydantic models for raw research data, defining the output of the Research Agent"""
from pydantic import BaseModel, Field


class ResearchData(BaseModel):
    """Structured research evidence collected by the Research Agent."""

    # Identified cryptocurrency
    coin_id: str
    coin_name: str
    coin_symbol: str

    # Requested historical analysis period
    period_days: int

    # Raw responses from research tools
    market_data: dict | None = None
    historical_data: dict | None = None
    news_data: list[dict] = Field(default_factory=list)

    # Errors encountered during data collection
    validation_error: str | None = None
    market_error: str | None = None
    historical_error: str | None = None
    news_error: str | None = None
