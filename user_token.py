from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends
from sqlalchemy.orm import Session
import models
import database
import schemas
from sqlalchemy.future import select

# Secret key for encoding/decoding JWT tokens
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# Algorithm used for JWT encoding/decoding
ALGORITHM = "HS256"
# Expiration time for access tokens (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def create_access_token(data: dict) -> str:
    """
    Create an access token with the provided data.

    Args:
        data (dict): The data to encode into the access token.

    Returns:
        str: The encoded access token.
    """
    # Make a copy of the data to encode
    to_encode = data.copy()

    # Calculate token expiration time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Update token payload with expiration time
    to_encode.update({"exp": expire})
    # Encode the token and return
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token: str, credentials_exception, db: Session = Depends(database.get_db)):
    """
    Verify the validity of the access token.

    Args:
        token (str): The access token to verify.
        credentials_exception: The exception to raise if token verification fails.
        db (Session, optional): The database session. Defaults to Depends(database.get_db).

    Raises:
        credentials_exception: If the token is invalid or verification fails.

    Returns:
        dict: The token data if verification is successful.
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract email from token payload
        email: str = payload.get("sub")
        # Query user from database based on email
        result = await db.execute(select(models.User).where(models.User.email == payload.get("sub")))
        user = result.scalars().first()
        # user = await db.execute(models.User.__table__.select().where(models.User.email == payload.get("sub")))
        # user = user.scalars().first()
        # If email is None or user not found, raise exception
        if email is None:
            raise credentials_exception
        # Create token data object and return
        token_data = dict(schemas.TokenData(email=email, user_id=user.user_id))
        return token_data
    except JWTError:
        raise credentials_exception
