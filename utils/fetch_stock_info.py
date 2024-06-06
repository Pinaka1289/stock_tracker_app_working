from nselib import capital_market
import httpx
import pandas as pd
import asyncio

# Cache for storing stock info
cache = {
    "stock_info": None,
    "last_fetched": None
}


async def get_company_logo(symbol):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://logo.clearbit.com/{symbol.lower()}.com')
            if response.status_code == 200:
                return f'https://logo.clearbit.com/{symbol.lower()}.com'
            else:
                return None
    except Exception:
        return None


async def fetch_nse_stock_info():
    # If cache is valid, return cached data
    if cache["stock_info"] is not None:
        return cache["stock_info"]

    # Get the list of all stock codes and company names
    equity_list = capital_market.equity_list()

    # Convert stock codes to a DataFrame
    df = equity_list

    # Fetch company logos asynchronously
    async def fetch_logo(symbol):
        logo = await get_company_logo(symbol)
        return logo

    logos = await asyncio.gather(*[fetch_logo(symbol) for symbol in df['SYMBOL']])
    df['LogoURL'] = logos

    # Cache the data
    cache["stock_info"] = df.to_dict(orient='records')
    cache["last_fetched"] = asyncio.get_event_loop().time()

    return cache["stock_info"]


async def refresh_stock_info_cache():
    while True:
        await fetch_nse_stock_info()
        # Refresh every 24 hours (86400 seconds)
        await asyncio.sleep(24 * 60 * 60)

# Start the cache refresh task
asyncio.create_task(refresh_stock_info_cache())
