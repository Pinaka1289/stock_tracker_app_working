from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
import asyncio
import models
import schemas
import database
import oauth2
from utils import fetch_live_stock_info, object_as_dict, fetch_stock_info
from sqlalchemy.future import select
from sqlalchemy import delete
from utils.fetch_live_stock_info import fetch_latest_price

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"]
)


async def fetch_live_data(db: Session, stock_data: models.TradeEntry):
    """
    Fetch live stock data asynchronously for a given stock.

    Args:
        db (Session): The database session.
        stock_data (models.TradeEntry): The stock data.

    Returns:
        Any: The live stock data.
    """
    live_data = await fetch_latest_price(
        stock_ticker=stock_data.stock_ticker, exchange=stock_data.trade_exchange)
    return live_data


async def fetch_all_stock(db: Session, current_user: schemas.User):
    """
    Fetch all stock data for the current user and append the latest stock price.

    Args:
        db (Session): The database session.
        current_user (schemas.User): The current user.

    Returns:
        List: A list of dictionaries containing the stock data and the latest stock price.
    """
    final_results = []
    try:
        all_stock_data = await db.execute(select(models.TradeEntry).where(models.TradeEntry.user_id == current_user.get('user_id')))
        all_stock_data = all_stock_data.scalars().all()

        tasks = [fetch_live_data(db, stock_data)
                 for stock_data in all_stock_data]
        live_data_results = await asyncio.gather(*tasks)
        # print(live_data_results)

        stock_info = await fetch_stock_info.fetch_nse_stock_info()

        stock_info_dict = {item['SYMBOL']: item for item in stock_info}

        for i, stock_data in enumerate(all_stock_data):
            stock_data_dict = object_as_dict.object_as_dict(stock_data)
            if live_data_results[i] is not None:
                stock_data_dict.update(live_data_results[i])

            matching_stock_info = stock_info_dict.get(stock_data.stock_ticker)
            if matching_stock_info:
                stock_data_dict.update(matching_stock_info)

            final_results.append(stock_data_dict)

        return final_results
    except Exception as e:
        print(f"An error occurred while fetching stock data: {e}")
        return None


@router.get("/all")
async def get_all_stock(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Fetch all stock data from the TradeEntry table for the current user and append the latest stock price.

    Args:
        db (Session, optional): The database session. Defaults to Depends(database.get_db).
        current_user (schemas.User, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Returns:
        List: A list of dictionaries containing the stock data and the latest stock price.
    """
    final_results = await fetch_all_stock(db, current_user)
    return final_results


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_stock(request: schemas.NewStock, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Create a new stock in the database.

    Args:
        request (schemas.NewStock): The information about the new stock.
        db (Session, optional): The database session. Defaults to Depends(database.get_db).
        current_user (schemas.User, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Raises:
        HTTPException: If the stock entry already exists.

    Returns:
        dict: A message indicating the stock entry was created successfully.
    """
    stock_info = await db.execute(select(models.TradeEntry).where(models.TradeEntry.stock_ticker == request.stock_ticker, models.TradeEntry.trade_entry_date == request.trade_entry_date))
    stock_info = stock_info.scalar()

    if stock_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Stock entry with stock_ticker '{request.stock_ticker}' and trade_entry_date '{request.trade_entry_date}' already exists")

    request.stock_ticker = request.stock_ticker.upper()
    request.trade_exchange = request.trade_exchange.upper()
    new_stock = models.TradeEntry(
        **request.dict(), user_id=current_user.get('user_id'))
    db.add(new_stock)
    await db.commit()
    return {"data": f"Stock entry with stock_ticker '{request.stock_ticker}' and trade_entry_date '{request.trade_entry_date}' created successfully"}


@router.get("/", status_code=status.HTTP_200_OK)
async def get_stock(stock_ticker: str, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Get stock data for a specific stock ticker.

    Args:
        stock_ticker (str): The stock ticker.
        db (Session, optional): The database session. Defaults to Depends(database.get_db).
        current_user (schemas.User, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Returns:
        List: A list of stock data for the specified stock ticker.
    """
    final_results = []
    stock_info = await db.execute(select(models.TradeEntry).where(models.TradeEntry.stock_ticker == stock_ticker.upper()))
    stock_info = stock_info.scalars().all()
    if not stock_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock with stock_ticker '{stock_ticker}' not found")

    tasks = [fetch_live_data(db, stock_data) for stock_data in stock_info]
    live_data_results = await asyncio.gather(*tasks)

    for i, stock_data in enumerate(stock_info):
        if live_data_results[i] is not None:
            stock_data_dict = object_as_dict.object_as_dict(stock_data)
            stock_data_dict['latest_price'] = live_data_results[i]
            final_results.append(stock_data_dict)
    print(final_results)
    return final_results


@router.get("/stock_tickers")
async def get_stock_tickers(current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Retrieve stock tickers.

    This endpoint fetches stock information from the NSE (National Stock Exchange)
    and returns a list of stock tickers and their corresponding company names.

    Parameters:
    - current_user: The current authenticated user.

    Returns:
    - A dictionary containing the list of stock tickers and company names.

    Example:
    {
        "stocks": [{"ticker": "AAPL", "company_name": "Apple Inc."}, {"ticker": "GOOGL", "company_name": "Google LLC"}, {"ticker": "AMZN", "company_name": "Amazon.com, Inc."}]
    }
    """
    try:
        stock_info = await fetch_stock_info.fetch_nse_stock_info()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to fetch stock info") from e

    if not stock_info:
        raise HTTPException(status_code=404, detail="No stock info found")

    try:
        stocks = [{"ticker": stock['SYMBOL'],
                   "company_name": stock['NAME OF COMPANY']} for stock in stock_info]
    except KeyError:
        raise HTTPException(
            status_code=500, detail="Invalid stock info format")

    return {"data": stocks}


@router.delete("/{trade_id}", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def delete_stock(trade_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Delete stock data for a specific stock ticker.

    Args:
        stock_ticker (str): The stock ticker.
        db (Session, optional): The database session. Defaults to Depends(database.get_db).
        current_user (schemas.User, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Returns:
        JSONResponse: HTTP 200 OK response with a success message.
    """
    result = await db.execute(delete(models.TradeEntry).where(models.TradeEntry.trade_id == trade_id))
    await db.commit()

    if result.rowcount:
        return {"message": f"Successfully deleted {result.rowcount} entries for trade_id {trade_id}"}
    else:
        raise HTTPException(
            status_code=404, detail="No entries found for the provided stock ticker")


@router.put("/{trade_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_stock(trade_id: int, request: schemas.NewStock, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Update stock data for a specific stock ticker.

    Args:
        stock_ticker (str): The stock ticker.
        request (schemas.NewStock): The information about the updated stock.
        db (Session, optional): The database session. Defaults to Depends(database.get_db).
        current_user (schemas.User, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Raises:
        HTTPException: If the stock with the specified stock_ticker is not found.

    Returns:
        dict: A message indicating the stock was updated successfully.
    """
    stock_info = await db.execute(models.TradeEntry.__table__.select().where(models.TradeEntry.trade_id == trade_id))
    stock_info = stock_info.scalar()
    if not stock_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock with stock_ticker '{trade_id}' not found")
    await db.execute(models.TradeEntry.__table__.update().where(models.TradeEntry.trade_id == trade_id).values(**request.dict()))
    await db.commit()
    return {"data": f"Stock with stock_ticker '{trade_id}' updated successfully"}
