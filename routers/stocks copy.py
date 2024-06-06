from utils import fetch_live_stock_info, object_as_dict
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
import models
import schemas
import database
import hashing
from sqlalchemy.orm import Session
import oauth2

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"]
)


@router.get("/all")
def get_all_stock(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Fetch all stock data from the TradeEntry table for the current user and append the latest stock price.

    Parameters:
    db (Session): The database session.
    current_user (schemas.User): The current user.

    Returns:
    list: A list of dictionaries containing the stock data and the latest stock price, or None if an error occurs.
    """
    # Initialize the final results list
    final_results = []

    try:
        # Fetch all stock data from the TradeEntry table for the current user
        all_stock_data = db.query(models.TradeEntry).filter(
            models.TradeEntry.user_id == current_user.get('user_id')).all()
        # print(all_stock_data)
        # Loop through all the stock data
        for stock_data in all_stock_data:
            # Fetch the latest stock price for the current stock
            # live_data = fetch_live_stock_info.fetch_live_stock_info(stock_data.stock_ticker).get('priceInfo').get('lastPrice')

            live_data = fetch_live_stock_info.fetch_latest_price(
                stock_ticker=stock_data.stock_ticker, exchange=stock_data.trade_exchange)
            # Check if the live data is not None
            if live_data is not None:
                # Convert the stock_data object to a dictionary
                stock_data_dict = object_as_dict.object_as_dict(stock_data)

                # Append the latest stock price to the stock data dictionary
                stock_data_dict['latest_price'] = live_data

                # Append the stock data dictionary to the final results
                final_results.append(stock_data_dict)

        # Return the final results
        return final_results
    except Exception as e:
        # Print the error message if an error occurs
        print(f"An error occurred while fetching stock data: {e}")
        # Return None if an error occurs
        return None


@ router.post("/", status_code=status.HTTP_201_CREATED)
def create_new_stock(request: schemas.NewStock, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Create a new stock in the database.

    This function creates a new stock in the database based on the information provided in the request.
    It first checks if the stock entry for the given date already exists. If the stock entry exists, it raises a 400 error.
    If the stock entry does not exist, it creates a new stock entry and commits the changes to the database.

    Args:
        request (schemas.NewStock): The information about the new stock.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the stock entry already exists.

    Returns:
        dict: A message indicating the stock entry was created successfully.
    """
    # Check if the stock entry for the given date already exists
    stock_info = db.query(models.TradeEntry).filter(
        models.TradeEntry.stock_ticker == request.stock_ticker,
        models.TradeEntry.trade_entry_date == request.trade_entry_date).first()

    # If the stock entry exists, raise a 400 error
    if stock_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Stock entry with stock_ticker '{request.stock_ticker}' and trade_entry_date '{request.trade_entry_date}' already exists")

    # Create a new stock entry
    new_stock = models.TradeEntry(
        **request.dict(), user_id=current_user.get('user_id'))
    db.add(new_stock)
    db.commit()

    # Return a success message
    return {"data": f"Stock entry with stock_ticker '{request.stock_ticker}' and trade_entry_date '{request.trade_entry_date}' created successfully"}


# @router.get("/stocks")
# def get_all_stock(db: Session = Depends(get_db)):
#     return {"data": db.query(models.TradeEntry).all()}


@ router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowStocks])
# @router.get("/stocks/", status_code=status.HTTP_200_OK)
def get_stock(stock_ticker: str, response: Response, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    stock_info = db.query(models.TradeEntry).filter(
        models.TradeEntry.stock_ticker == stock_ticker).all()
    if not stock_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock with stock_ticker '{stock_ticker}' not found")
    # return {"data": stock_info}
    return stock_info


# add stock delete request
@ router.delete("/{stock_ticker}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(stock_ticker: str, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    stock_info = db.query(models.TradeEntry).filter(
        models.TradeEntry.stock_ticker == stock_ticker).delete(synchronize_session=False)
    if not stock_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock with stock_ticker '{stock_ticker}' not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# add stock update request


@ router.put("/{stock_ticker}", status_code=status.HTTP_202_ACCEPTED)
def update_stock(stock_ticker: str, request: schemas.NewStock, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    stock_info = db.query(models.TradeEntry).filter(
        models.TradeEntry.stock_ticker == stock_ticker).first()
    if not stock_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock with stock_ticker '{stock_ticker}' not found")
    db.query(models.TradeEntry).filter(models.TradeEntry.stock_ticker == stock_ticker).update(
        request.dict(), synchronize_session=False)
    db.commit()
    return {"data": f"Stock with stock_ticker '{stock_ticker}' updated successfully"}
