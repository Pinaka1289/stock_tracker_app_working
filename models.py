from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TradeEntry(Base):
    """
    Model representing trade entry.
    """
    __tablename__ = "trade_entry"

    trade_id = Column(Integer, primary_key=True, index=True)
    stock_ticker = Column(String(50), index=True)
    trade_exchange = Column(String(50))
    trade_entry_date = Column(Date)  # Date column for trade entry date
    quantity = Column(Integer)
    price_per_stock = Column(Float)  # Adjusted column name
    trade_total_price = Column(Float)
    target_price = Column(Float)
    trade_strategy = Column(String(255))  # Adjust length as needed

    # Create a relationship between TradeEntry and User
    user_id = Column(Integer, ForeignKey('users.user_id'))
    creator = relationship("User", back_populates="trade_entries")


class User(Base):
    """
    Model representing a user.
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))  # Store hashed password

    # Define relationship with TradeEntry
    trade_entries = relationship("TradeEntry", back_populates="creator")

    def verify_password(self, password: str) -> bool:
        """
        Verify if the provided password matches the stored hashed password.

        Args:
            password (str): The password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return pwd_context.verify(password, self.password_hash)

    def set_password(self, password: str):
        """
        Hash and set the user's password.

        Args:
            password (str): The password to hash and set.
        """
        self.password_hash = pwd_context.hash(password)
