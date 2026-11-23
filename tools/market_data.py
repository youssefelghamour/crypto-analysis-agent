import json
import requests
from langchain_core.tools import tool


@tool
def crypto_list_tool(limit: int = 10) -> str:
    """
    Fetches the available cruptocurrencies from CoinGecko API
    
    Args: 
        limit (int): max number of coins to return
        
    Returns:
        str: JSON string with a list of coins: [{"id": "...", "symbol": "...", "name": "..."}, ...]
    """
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/list",
            timeout=30
        )
        # Raise an exception for HTTP errors (4xx and 5xx)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return json.dumps({
            "status": False,
            "error": f"CoinGecko API HTTP error: {e}"
        })
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": False,
            "error": f"CoinGecko API request failed: {e}"
        })

    try:
        coins = response.json()
    except ValueError:
        return json.dumps({
            "status": False,
            "error": "Invalid JSON from CoinGecko API list"
        })

    return json.dumps({
        "status": True,
        "coins": coins[:limit]
    }, indent=2)



@tool
def crypto_search_tool(query: str) -> str:
    """
    Searches the cruptocurrency list by name, symbol or id
    Use this tool to find the coin id before requesting market data instead of
    retrieving the whole cryptocurrency list to reduce the context
    
    Args: 
        query (str): search query
        
    Returns:
        str: JSON string with a list of coins: [{"id": "...", "symbol": "...", "name": "..."}, ...]
    """
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": query},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # result include other lists than coins, keep only coin with only id, sym & name
        coins = [
            {
                "id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"]
            }
            for coin in data.get("coins", [])[:10]
        ]

        if not coins:
            return json.dumps({
                "status": False,
                "error": f"No cryptocurrencies found for: {query}"
            }, indent=2)

        return json.dumps({
            "status": True,
            "query": query,
            "coins": coins
        }, indent=2)

    except requests.exceptions.HTTPError as e:
        return json.dumps({
            "status": False,
            "error": f"CoinGecko API error: {e}"
        }, indent=2)

    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": False,
            "error": f"Request failed: {e}"
        }, indent=2)

    except ValueError:
        return json.dumps({
            "status": False,
            "error": "Invalid JSON response from CoinGecko"
        }, indent=2)



@tool
def crypto_data_tool(coin_id: str) -> str:
    """
    Fetches market information about a specific cryptocurrency
    
    Args:
        coin_id (str): the id of the cryptocurrency
    
    Returns:
        str: JSON string
    """
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": coin_id
            },
            timeout=30
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        return json.dumps({
            "status": False,
            "error": f"CoinGecko API HTTP error: {e}"
        })

    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": False,
            "error": f"CoinGecko API request failed: {e}"
        })

    try:
        data = response.json()
    except ValueError:
            return json.dumps({
                "status": False,
                "error": f"Failed to retrieve data about {coin_id} from CoinGecko API"
            })

    if not data:
        # If the coin id doesn't exits the API returns an empty list
         return json.dumps({
                "status": False,
                "error": f"No market data found for coin: {coin_id}"
             }, indent=2)
    else:
        return json.dumps({
            "status": True,
            "coin": data[0]  # API returns a list even when requsting one coin
        }, indent=2)



@tool
def crypto_history_tool(coin_id: str, days: int = 7) -> str:
    """
    Fetches historical price and trading volume data for a cryptocurrency.

    Args:
        coin_id: CoinGecko cryptocurrency ID (e.g. bitcoin).
        days: Number of days of history (1, 7, 14, or 30).

    Returns:
        JSON string containing historical prices and volumes.
    """

    if days not in [1, 7, 14, 30]:
        return json.dumps({
            "status": False,
            "error": "Days must be 1, 7, 14, or 30."
        })

    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={
                "vs_currency": "usd",
                "days": days
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": False,
            "error": f"CoinGecko API request failed: {e}"
        })

    except ValueError:
        return json.dumps({
            "status": False,
            "error": "Invalid JSON response from CoinGecko."
        })

    prices = [
        {
            "timestamp": timestamp,
            "price": price
        }
        for timestamp, price in data.get("prices", [])
    ]

    volumes = [
        {
            "timestamp": timestamp,
            "volume": volume
        }
        for timestamp, volume in data.get("total_volumes", [])
    ]

    if not prices:
        return json.dumps({
            "status": False,
            "error": f"No historical data found for {coin_id}."
        })

    price_values = [item["price"] for item in prices]

    first_price = price_values[0]
    last_price = price_values[-1]

    statistics = {
        "starting_price": first_price,
        "latest_price": last_price,
        "price_change": round(last_price - first_price, 2),
        "price_change_percentage": round(
            ((last_price - first_price) / first_price) * 100, 2
        ),
        "highest_price": max(price_values),
        "lowest_price": min(price_values)
    }

    return json.dumps({
        "status": True,
        "coin_id": coin_id,
        "currency": "USD",
        "period_days": days,
        "prices": prices,
        "volumes": volumes,
        "statistics": statistics
    }, indent=2)