"""Python metrics node for transforming raw cryptocurrency research data

The node consumes the market_data and historical_data fields populated
by the research subgraph's map_research_data node into the state

It extracts current market indicators from CoinGecko's market response
and calculates additional indicators from historical price and volume

The resulting MarketMetrics object is stored in AnalysisState.metrics
The original research data and historical time series remain unchanged
"""

from statistics import mean, pstdev
from graphs.state import AnalysisState
from schemas.report import MarketMetrics


def to_float(value):
    """Convert a value to float, returning None if unavailable or invalid"""
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def metrics_node(state: AnalysisState) -> dict:
    """Extract and calculate market metrics from the research results"""

    market_data = state.get("market_data") or {}
    historical_data = state.get("historical_data") or {}

    # Extract the current market snapshot returned by CoinGecko
    coin = market_data.get("coin") or {}

    current_price = to_float(coin.get("current_price"))
    market_cap = to_float(coin.get("market_cap"))
    volume_24h = to_float(coin.get("total_volume"))
    price_change_24h = to_float(
        coin.get("price_change_percentage_24h")
    )

    # Extract valid historical price observations
    prices = [
        price
        for point in historical_data.get("prices", [])
        if (price := to_float(point.get("price"))) is not None
    ]

    # Extract valid historical 24-hour volume observations
    volumes = [
        volume
        for point in historical_data.get("volumes", [])
        if (volume := to_float(point.get("volume"))) is not None
    ]

    # Calculate indicators from historical prices
    period_change = None
    period_high = None
    period_low = None
    average_price = None
    price_volatility = None

    if prices:
        period_high = max(prices)
        period_low = min(prices)
        average_price = mean(prices)

    if len(prices) >= 2 and prices[0] != 0:
        period_change = (
            (prices[-1] - prices[0]) / prices[0]
        ) * 100

    # Calculate the standard deviation of consecutive percentage returns
    # Percentage change between each price and the price before it
    returns = []

    for previous, current in zip(prices, prices[1:]):
        if previous != 0:
            percentage_return = (
                (current - previous) / previous
            ) * 100

            returns.append(percentage_return)

    # Require at least two observations to calculate return volatility
    if len(returns) >= 2:
        """population standard deviation: measures how spread out the percentage changes are
            - Returns: [1%, 2%, 3%] : changes are relatively close/consistent, low pstdev = low price volatility
            - Returns: [-10%, 5%, 20%] : changes are spread out, high pstdev = high price volatility
        """
        price_volatility = pstdev(returns)

    # Historical volumes are rolling 24-hour observations
    # Calculate their average instead of summing and double counting them
    average_volume = mean(volumes) if volumes else None

    metrics = MarketMetrics(
        current_price_usd=current_price,
        market_cap_usd=market_cap,
        total_volume_24h_usd=volume_24h,
        price_change_24h_pct=price_change_24h,
        period_change_pct=period_change,
        period_high_usd=period_high,
        period_low_usd=period_low,
        average_price_usd=average_price,
        price_volatility_pct=price_volatility,
        average_volume_24h_usd=average_volume,
    )

    return {"metrics": metrics}
