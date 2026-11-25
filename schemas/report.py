"""Pydantic models for the final cryptocurrency market report
Defining the output of the complete report workflow
The final MarketReport is assembled after research, metrics calculation, analysis & review
"""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    timestamp: datetime
    price_usd: float


class VolumePoint(BaseModel):
    timestamp: datetime
    volume_usd: float


class MarketMetrics(BaseModel):
    current_price_usd: float | None = None
    market_cap_usd: float | None = None
    total_volume_24h_usd: float | None = None
    price_change_24h_pct: float | None = None

    period_change_pct: float | None = None
    period_high_usd: float | None = None
    period_low_usd: float | None = None


class NewsArticle(BaseModel):
    title: str
    source: str | None = None
    url: str
    published_at: datetime | None = None


class MarketAnalysis(BaseModel):
    """LLM generated analysis based on the previous results using tools"""
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    outlook: str
    confidence: Literal["low", "medium", "high"]
    confidence_reason: str


class MarketReport(BaseModel):
    """Final validated report delivered to the user and consumed by the frontend"""
    # Currency being analyzed
    coin_id: str
    coin_name: str
    coin_symbol: str

    # Analysis period and generation time
    period_days: int
    generated_at: datetime

    # Dashboard data
    metrics: MarketMetrics
    price_history: list[PricePoint]
    volume_history: list[VolumePoint]
    news: list[NewsArticle]

    # LLM-generated interpretation analysis
    analysis: MarketAnalysis

    # Data transparency
    data_sources: list[str] = Field(default_factory=list)
    # Tells the user when data is incomplete or unavailable
    limitations: list[str] = Field(default_factory=list)
