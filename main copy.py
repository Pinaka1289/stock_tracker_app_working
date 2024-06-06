from fastapi import Depends, FastAPI
from typing import Optional
import models
import schemas
import database
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/")
def read_root():
    return {"data": {"Hello": "World"}}


@app.get("/stocks")
def read_item(limit=10, all: bool = True, sort: Optional[str] = None):
    # return {"data": {"stocks": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]}}
    if all:
        return {"data": {"stocks": f"{limit} both buy and sell stocks information"}}
    else:
        return {"data": {"stocks": f"{limit} only buy stocks information"}}


@app.get("/stocks/{stock}")
def read_item(stock: str, q: str = None):
    return {"stock": stock, "q": q}


@app.get("/stocks/{stock}/price")
def read_item(stock: str, limit=10):
    return {"stock": stock, "price": 100}


@app.post("/stocks")
def create_item(request: schemas.NewStock, db: Session = Depends(get_db)):
    new_stock = models.TradeEntry(stock_ticker=request.stock_ticker,
                                  trade_exchange=request.trade_exchange,
                                  trade_entry_date=request.trade_entry_date,
                                  quantity=request.quantity,
                                  trade_entry_price_per_stock=request.trade_entry_price_per_stock,
                                  trade_total_price=request.trade_total_price,
                                  target_price=request.target_price,
                                  trade_strategy=request.trade_strategy)
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock
