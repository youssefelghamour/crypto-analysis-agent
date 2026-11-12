import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://api.coingecko.com/api/v3"

"""
headers = {
    "x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY")
}
"""


def print_response(title, data):
    print(f"\n--- {title} ---")
    print(json.dumps(data, indent=2))


# 1. Get cryptocurrency coins list
response = requests.get(
    f"{BASE_URL}/coins/list",
    # headers=headers,
    timeout=30
)
response.raise_for_status()
coins = response.json()
print_response("Crypto List", coins[:5])


# 2. Get Bitcoin market data
response = requests.get(
    f"{BASE_URL}/coins/markets",
    # headers=headers,
    params={
        "vs_currency": "usd",
        "ids": "bitcoin"
    },
    timeout=30
)
response.raise_for_status()
market_data = response.json()
print_response("Bitcoin Market Data", market_data)


# 3. Get Bitcoin news from GDELT API
response = requests.get(
    "https://api.gdeltproject.org/api/v2/doc/doc",
    params={
        "query": "bitcoin",
        "mode": "artlist",
        "format": "json",
        "maxrecords": 10,
        "timespan": "7d"
    },
    timeout=30
)
response.raise_for_status()
news = response.json()
print_response("Bitcoin News", news)
