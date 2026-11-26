"""FastAPI API for the cryptocurrency analysis agent"""
from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from graphs.main_graph import build_main_graph
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import time
import httpx
import asyncio


app = FastAPI(
    title="Crypto Analysis Agent API",
    description="Generate cryptocurrency reports and discuss market conditions",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Build the graph once when the API starts
agent, db_connection = build_main_graph()


class AgentRequest(BaseModel):
    """Request body for interacting with the agent"""
    message: str = Field(min_length=1)
    thread_id: str | None = None


@app.get("/health")
def health_check():
    """Check if the API is running"""
    return {"status": "ok"}


@app.post("/agent")
def interact_with_agent(request: AgentRequest):
    """Invokes the main agentic workflow with the user message"""

    thread_id = request.thread_id or str(uuid4())

    result = agent.invoke(
        {
            "request": request.message,
            "messages": [HumanMessage(content=request.message)],
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    if result.get("intent") == "report":
        response = jsonable_encoder(result.get("final_report"))
    else:
        response = result.get("discussion_response")

    return {
        "thread_id": thread_id,
        "intent": result.get("intent"),
        "response": response,
    }



COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"

# In-memory cache for the API call
ticker_cache = {
    "data": None,     # stores the last successful API response
    "updated_at": 0,  # when we fetched it
}

# How long the cached result remains valid (60 sec)
TICKER_CACHE_TTL = 60


@app.get("/market/ticker")
async def get_market_ticker():
    """Return the top 10 cryptocurrencies data for the market ticker"""
    now = time.monotonic()

    # Return cached result if it exists and is less than 60 seconds old
    if (
        ticker_cache["data"] is not None
        and now - ticker_cache["updated_at"] < TICKER_CACHE_TTL
    ):
        return ticker_cache["data"]

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",  # sort by market cap, highest first
        "per_page": 10,              # return 10 results
        "page": 1,                   # retrieve thefirst page
        "sparkline": "false",        # to not include mini chart data
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                COINGECKO_MARKETS_URL,
                params=params,
            )
            response.raise_for_status()

        coins = response.json()

        # convert & format CoinGecko's json response into a list of defined dicts
        result = {
            "assets": [
                {
                    "id": coin["id"],
                    "image": coin["image"],
                    "name": coin["name"],
                    "symbol": coin["symbol"].upper(),
                    "price_usd": coin["current_price"],
                    "change_24h": coin["price_change_percentage_24h"],
                }
                for coin in coins
            ],
            "updated_at": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(),
            ),
        }

        # Cache the result
        ticker_cache["data"] = result
        ticker_cache["updated_at"] = now

        return result

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve market data from CoinGecko.",
        )


HISTORY_CACHE_TTL = 300

# Cached result for 300 sec (5min)
history_cache = {
    "data": None,
    "updated_at": 0,
}

# List of the coinc we decided to include
FEATURED_COIN_IDS = [
    "bitcoin",
    "ethereum",
    "solana",
    "ripple",
]


@app.get("/market/history")
async def get_market_history():
    """Return 7 days of price history for selected cryptocurrencies to display the graph"""
    now = time.monotonic()

    # Return cached result if available
    if (
        history_cache["data"] is not None
        and now - history_cache["updated_at"] < HISTORY_CACHE_TTL
    ):
        return history_cache["data"]

    async def fetch_coin_history(client, coin_id):
        """Get historical prices and calculate percentage changes"""
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"

        response = await client.get(
            url,
            params={
                "vs_currency": "usd",
                "days": 7,
            },
        )
        response.raise_for_status()

        # The response includes 3 objects, list of prices, market caps, and total volumes
        prices = response.json()["prices"]

        if not prices:
            raise ValueError(f"No historical prices returned for {coin_id}")

        # index 0 is the timestamp, each item in prices is [timestamp, price]
        starting_price = prices[0][1]

        return {
            "id": coin_id,
            "prices": [
                {
                    "timestamp": timestamp,
                    "price_usd": price,
                    "change_pct": round(
                        ((price / starting_price) - 1) * 100,
                        4,
                    ),
                }
                for timestamp, price in prices
            ],
        }

    try:
        # assets = [ {'id': 'bitcoin', 'prices': [...]}, {'id': 'ethereum', 'prices': [...]}, ... ]
        async with httpx.AsyncClient(timeout=20.0) as client:
            assets = await asyncio.gather(
                *[
                    fetch_coin_history(client, coin_id)
                    for coin_id in FEATURED_COIN_IDS
                ]
            )

        result = {
            "period": "7d",
            "assets": assets,
            "updated_at": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(),
            ),
        }

        history_cache["data"] = result
        history_cache["updated_at"] = now

        return result

    except (httpx.HTTPError, ValueError, KeyError) as error:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve historical market data: {error}",
        )
