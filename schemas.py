from typing import List, Optional
from pydantic import BaseModel
from datetime import date


class Login(BaseModel):
    username: str
    password: str


class NewStock(BaseModel):
    stock_ticker: str
    trade_exchange: str
    trade_entry_date: date
    quantity: int
    price_per_stock: float
    trade_total_price: float
    target_price: float
    trade_strategy: str
    # user_id: int


# This below class will be used in get method to return only elements in the class


class ShowStocksInfo(BaseModel):
    stock_ticker: str
    trade_exchange: str
    trade_entry_date: date

    class Config():
        orm_mode = True


class User(BaseModel):
    username: str
    email: str
    password: str


class ShowUser(BaseModel):
    username: str
    email: str
    # trade_entries: Optional[List[NewStock]] = None

    class Config():
        orm_mode = True


class ShowUserStocks(BaseModel):
    username: str
    email: str
    trade_entries: List[NewStock] = []
    # trade_entries: Optional[List[NewStock]] = None

    class Config():
        orm_mode = True

# This below class will be used in get method to return only elements in the class


class ShowStocks(NewStock):
    creator: ShowUser

    class Config():
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
