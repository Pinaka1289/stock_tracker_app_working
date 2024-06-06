# import nselib

# # data = nselib.trading_holiday_calendar()
# # print(data)

# print(dir(nselib))
import yfinance as yf
from bs4 import BeautifulSoup
import requests
from jugaad_data.nse import NSELive
import json
import aiohttp
import asyncio
from nselib import capital_market

nse_live_connection = NSELive()


# def fetch_live_stock_info(symbol: str):
#     """
#     Fetch live stock data for a given symbol using the jugaad_data library.

#     Parameters:
#     symbol (str): The symbol of the stock to fetch data for.

#     Returns:
#     pandas.DataFrame: A DataFrame containing the live stock data.
#     """
#     try:
#         # Fetch the live stock data
#         live_data = nse_live_connection.stock_quote(symbol)
#         return live_data
#     except Exception as e:
#         # If an error occurs, print the error message and return None
#         print(f"An error occurred while fetching live stock data for {
#               symbol}: {e}")
#         return None


# # Test the function with the symbol 'INFY'
# live_stock_price_info = fetch_live_stock_info('INFY').get('priceInfo')
# print(json.dumps(live_stock_price_info, indent=4))
# last_price = live_stock_price_info.get('lastPrice')
# print(last_price)


async def fetch_latest_price(stock_ticker, exchange="NSE"):
    """
    Fetch the live stock information including current price, change in price, and percentage change.

    Parameters:
    stock_ticker (str): The stock ticker symbol.
    exchange (str): The exchange where the stock is listed.

    Returns:
    dict: A dictionary containing the current price, change in price, and percentage change.
    """
    symbol = f"{stock_ticker}.NS"
    stock = yf.Ticker(symbol)
    info = stock.info

    current_price = info.get('currentPrice')
    previous_close = info.get('previousClose')

    if current_price is not None and previous_close is not None:
        price_change = current_price - previous_close
        percentage_change = (price_change / previous_close) * 100

        current_price_str = f"₹{current_price:.2f}"
        price_change_str = f"{'+' if price_change >
                              0 else ''}{price_change:.2f}"
        percentage_change_str = f"{
            '+' if percentage_change > 0 else ''}{percentage_change:.2f}%"
    else:
        current_price_str = None
        price_change_str = None
        percentage_change_str = None

    return {
        'current_price': current_price_str,
        'price_change': price_change_str,
        'percentage_change': percentage_change_str
    }

# Example usage
# Fetch info for Reliance Industries Ltd. on NSE
# stock_info = fetch_live_stock_info("RELIANCE.NS")
# print(stock_info)


async def fetch_indices():
    indices_data = capital_market.market_watch_all_indices()

    # Filter the data for the required indices
    required_indices = ['NIFTY 50', 'INDIA VIX', 'NIFTY BANK']
    filtered_data = indices_data[indices_data['index'].isin(required_indices)]

    indices_info = {}

    for _, row in filtered_data.iterrows():
        index_info = {
            'value': row['last'],
            'change': row['variation'],
            'change_percent': row['percentChange']
        }
        indices_info[row['index']] = index_info

    return indices_info
