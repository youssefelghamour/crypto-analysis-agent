import json
import requests
import os

from dotenv import load_dotenv
from typing import Optional

from langchain_core.tools import tool
from langchain_groq import ChatGroq

import xml.etree.ElementTree as ET


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=0
)


@tool
def crypto_list_tool(limit: int = 25) -> str:
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

# print(crypto_list_tool.invoke({"limit": 5}))


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

# print(crypto_data_tool.invoke({"coin_id": "bitcoin"}))


def fetch_google_new(query, max_items):
    """Fetches articles from Google NEws RSS
    
    Args:
        query (str): a search query string including the name of the cryptocurrency
        max_items (int): the number of news articles to retrieve
    
    Return:
        str: JSON string containing a list of articles
    """
    try:
        response = requests.get(
            "https://news.google.com/rss/search",
            params={
                "q": f"{query} when:7d",  # Search query
                "hl": "en-US",            # Language
                "gl": "US",               # Country
                "ceid": "US:en"           # Edition
            },
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": False,
            "provider": "Google News",
            "error": f"Google News request failed: {e}"
        })

    # Google News returns XML (RSS), not JSON
    try:
        # Convert the XML response bytes into a Python XML tree
        # root is the top level rss element
        root = ET.fromstring(response.content)

    # If the response isn't valid XML, parsing fails
    except ET.ParseError:
        return json.dumps({
            "status": False,
            "provider": "Google News",
            "error": "Invalid XML response from Google News"
        })

    articles = []

    # Find every <item> element inside <channel>
    # Each <item> is one news article
    for item in root.findall("./channel/item")[:max_items]:
        # Find the article's <source> element, may not exist in every article
        source = item.find("source")

        articles.append({
            "title": item.findtext("title"),
            "url": item.findtext("link"),
            "source": source.text if source is not None else None,
            "published_at": item.findtext("pubDate")
        })

    if not articles:
        return json.dumps({
            "status": False,
            "provider": "Google News",
            "query": query,
            "error": f"No articles found for {query}"
        }, indent=2)

    return json.dumps({
        "status": True,
        "provider": "Google News",
        "query": query,
        "articles": articles
    }, indent=2)


@tool
def crypto_news_tool(query: str, max_items: int = 10) -> str:
    """
    Fetches a number of the most recent articles (last 7 days) about the specified cryptocurrency
    uses GDELT API as default and Google News RSS as fallback if GDELT fails or reaches the rate limit we 
    
    Args:
        query (str): a search query string including the name of the cryptocurrency
        max_items (int): the number of news articles to retrieve
    
    Return:
        str: JSON string containing a list of articles
    """
    try:
        response = requests.get(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params = {
                "query": query,
                "mode": "artlist",
                "format": "json",
                "maxrecords": max_items,
                "timespan": "7d"
            },
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429 or response.status_code >= 500:
            # Switch to Google News RSS
            return fetch_google_new(query, max_items)
        
        return json.dumps({
            "status": False,
            "provider": "GDELT",
            "error": f"GDELT API HTTP error: {e}"
        })
    
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": False,
            "provider": "GDELT",
            "error": f"GDELT API request failed: {e}"
        })

    try:
        articles = response.json()
    except ValueError:
        return json.dumps({
            "status": False,
            "provider": "GDELT",
            "error": f"Failed to retrieve articles about {query} from GDELT API",
            "http_status": response.status_code,
            "response": response.text[:500]
        })

    if not articles:
        # If no articles were found
        return json.dumps({
            "status": False,
            "provider": "GDELT",
            "query": query,
            "error": f"No market articles found for {query}"
        }, indent=2)
    else:
        return json.dumps({
            "status": True,
            "provider": "GDELT",
            "query": query,
            "articles": articles
        }, indent=2)

# print(crypto_news_tool.invoke({"query": 'bitcoin', "max_items": 5}))