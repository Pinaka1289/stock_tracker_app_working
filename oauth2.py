from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models
import database
import user_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(data: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Get the current user based on the provided access token.

    Args:
        data (str, optional): The access token. Defaults to Depends(oauth2_scheme).
        db (Session, optional): The database session. Defaults to Depends(database.get_db).

    Raises:
        HTTPException: If credentials are invalid or token verification fails.

    Returns:
        dict: The token data if verification is successful.
    """
    # Define exception for invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Verify token and return token data
    return await user_token.verify_token(data, credentials_exception, db=db)
