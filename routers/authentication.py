from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db as get_db_async
from models import User
from hashing import Hash
import user_token
from sqlalchemy.future import select
import models

router = APIRouter(
    prefix='/login',
    tags=['Authentication']
)


@router.post('/')
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_async)):
    """
    Endpoint for user login.

    This endpoint authenticates users by checking their email and password.
    If the provided credentials are correct, it generates and returns an access token.

    Args:
        request (OAuth2PasswordRequestForm): The login request containing the username and password.
        db (Session, optional): The async database session. Defaults to Depends(get_db_async).

    Raises:
        HTTPException: If the credentials are invalid or the password is incorrect.

    Returns:
        dict: The access token.`
    """
    # Check if the user with the provided email exists
    result = await db.execute(select(models.User).where(models.User.email == request.username))
    user = result.scalars().first()

    # If the user doesn't exist or the password is incorrect, raise an HTTPException
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid Credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Incorrect Password")
    # Generate and return an access token
    access_token = await user_token.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}
