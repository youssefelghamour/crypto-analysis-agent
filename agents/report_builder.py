"""Python node responsible for assembling the final cryptocurrency report"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from graphs.state import AnalysisState
from schemas.report import (
    MarketReport,
    MarketMetrics,
    MarketAnalysis,
    PricePoint,
    VolumePoint,
    NewsArticle,
)


def parse_timestamp(value):
    """Convert timestamp formats into a UTC datetime"""
    if value is None:
        return None

    try:
        # CoinGecko timestamps are milliseconds since Unix epoch
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value / 1000, tz=timezone.utc)

        # GDELT timestamp format: YYYYMMDDTHHMMSSZ
        if isinstance(value, str) and len(value) == 16 and value.endswith("Z"):
            return datetime.strptime(
                value, "%Y%m%dT%H%M%SZ"
            ).replace(tzinfo=timezone.utc)

        # Try ISO 8601 first
        if isinstance(value, str):
            try:
                timestamp = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                # Google News RSS uses RFC 2822 dates
                timestamp = parsedate_to_datetime(value)

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            return timestamp.astimezone(timezone.utc)

    except (ValueError, TypeError, OverflowError):
        return None

    return None


def build_price_history(historical_data):
    """Convert raw CoinGecko prices into Pydantic PricePoint objects"""
    history = []

    for point in (historical_data or {}).get("prices", []):
        timestamp = parse_timestamp(point.get("timestamp"))
        price = point.get("price")

        if timestamp is None or price is None:
            continue

        try:
            history.append(
                PricePoint(timestamp=timestamp, price_usd=float(price))
            )
        except (ValueError, TypeError):
            continue

    return history


def build_volume_history(historical_data):
    """Convert raw CoinGecko volumes list into VolumePoint objects"""
    history = []

    for point in (historical_data or {}).get("volumes", []):
        timestamp = parse_timestamp(point.get("timestamp"))
        volume = point.get("volume")

        if timestamp is None or volume is None:
            continue

        try:
            history.append(
                VolumePoint(timestamp=timestamp, volume_usd=float(volume))
            )
        except (ValueError, TypeError):
            continue

    return history


def build_news_articles(news_data):
    """Normalize GDELT and Google News articles into NewsArticle objects"""
    articles = []

    for article in news_data or []:
        title = article.get("title")
        url = article.get("url") or article.get("link")

        # A title and URL are required by the NewsArticle schema
        if not title or not url:
            continue

        published_at = parse_timestamp(
            article.get("published_at") or article.get("seendate")
        )

        source = (
            article.get("source")
            or article.get("domain")
        )

        articles.append(
            NewsArticle(
                title=title,
                source=source,
                url=url,
                published_at=published_at,
            )
        )

    return articles


def report_builder_node(state: AnalysisState) -> dict:
    """Assemble the final MarketReport from research and analysis results"""

    historical_data = state.get("historical_data") or {}
    news_data = state.get("news_data") or {}

    metrics = state["metrics"]
    analysis = state["analysis"]

    # Making sure to convert dicts into their corresponding Pydantic models
    if isinstance(metrics, dict):
        metrics = MarketMetrics.model_validate(metrics)

    if isinstance(analysis, dict):
        analysis = MarketAnalysis.model_validate(analysis)

    price_history = build_price_history(historical_data)
    volume_history = build_volume_history(historical_data)
    news = build_news_articles(news_data)

    limitations = []

    # Preserve errors encountered during research.
    error_fields = {
        "validation": "validation_error",
        "market data": "market_error",
        "historical data": "historical_error",
        "news": "news_error",
    }

    for label, field in error_fields.items():
        error = state.get(field)
        if error:
            limitations.append(f"{label.capitalize()}: {error}")

    # Report missing data even when no explicit error was returned
    if not state.get("market_data"):
        limitations.append("Current market data is unavailable.")

    if not historical_data.get("prices"):
        limitations.append("Historical price data is unavailable.")

    if not historical_data.get("volumes"):
        limitations.append("Historical volume data is unavailable.")

    if not news:
        limitations.append("No valid news articles are available.")

    # Identify sources only when their data is available
    data_sources = []

    if state.get("market_data") or historical_data:
        data_sources.append("CoinGecko")

    report = MarketReport(
        coin_id=state["coin_id"],
        coin_name=state["coin_name"],
        coin_symbol=state["coin_symbol"],
        period_days=state["period_days"],
        generated_at=datetime.now(timezone.utc),
        metrics=metrics,
        price_history=price_history,
        volume_history=volume_history,
        news=news,
        news_provider=state.get("news_provider"),
        analysis=analysis,
        data_sources=data_sources,
        limitations=limitations,
    )

    return {
        "final_report": report,
        "status": "completed",
    }
