import aiohttp
import asyncio
from nselib import capital_market
from fastapi import HTTPException
import requests
from bs4 import BeautifulSoup


async def fetch_main_indices():
    """
    Fetch main indices from the market.

    This function fetches market indices data, filters it for the required indices,
    and returns a dictionary with the index name as the key and a dictionary of index info as the value.

    Returns:
    - A dictionary containing the index info for each required index.

    Example:
    {
        "NIFTY 50": {"value": 17300.15, "change": -29.20, "change_percent": -0.17},
        "INDIA VIX": {"value": 20.5875, "change": 0.20, "change_percent": 0.98},
        "NIFTY BANK": {"value": 36552.00, "change": -112.20, "change_percent": -0.31},
        "SENSEX": {"value": 58000.00, "change": -150.00, "change_percent": -0.26}
    }
    """
    try:
        # Fetch market indices data
        indices_data = capital_market.market_watch_all_indices()
    except Exception as e:
        # If an exception occurs during fetching, raise an HTTPException
        raise HTTPException(
            status_code=500, detail="Failed to fetch market indices") from e

    # Filter the data for the required indices
    required_indices = ['NIFTY 50', 'NIFTY BANK']
    # required_indices = ['NIFTY 50', 'INDIA VIX', 'NIFTY BANK']
    filtered_data = indices_data[indices_data['index'].isin(required_indices)]

    indices_info = {}

    try:
        # Iterate over the filtered data
        for _, row in filtered_data.iterrows():
            # Create a dictionary of index info for each row
            index_info = {
                'value': row['last'],
                'change': row['variation'],
                'change_percent': row['percentChange']
            }
            # Add the index info to the indices_info dictionary with the index name as the key
            indices_info[row['index']] = index_info
    except KeyError as e:
        # If a KeyError occurs during iteration, raise an HTTPException
        raise HTTPException(
            status_code=500, detail=f"Invalid data format: {str(e)}") from e

    # Fetch SENSEX data from Yahoo Finance
    try:
        url = "https://finance.yahoo.com/quote/%5EBSESN"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            sensex_value = soup.find(
                'fin-streamer', {'data-field': 'regularMarketPrice'}).text
            sensex_change = soup.find(
                'fin-streamer', {'data-field': 'regularMarketChange'}).text
            sensex_change_percent = soup.find(
                'fin-streamer', {'data-field': 'regularMarketChangePercent'}).text

            indices_info["SENSEX"] = {
                'value': sensex_value,
                'change': sensex_change,
                'change_percent': sensex_change_percent
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to fetch SENSEX data from Yahoo Finance")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to fetch SENSEX data") from e

    # Return the indices_info dictionary
    return indices_info
