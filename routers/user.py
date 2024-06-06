from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models
import schemas
import database
import hashing
from utils import email_service

router = APIRouter(
    prefix="/signup",
    tags=["users"]
)

# Create a new user


@router.post('/', response_model=schemas.ShowUser)
async def create_user(request: schemas.User, db: AsyncSession = Depends(database.get_db)):
    """
    Create a new user.

    Args:
        request (schemas.User): The user data to create.
        db (AsyncSession, optional): The async database session. Defaults to Depends(database.get_db).

    Returns:
        schemas.ShowUser: The created user data.
    """
    try:
        new_user = models.User(
            username=request.username,
            email=request.email,
            password=hashing.Hash.bcrypt(request.password)
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Send registration email
        await email_service.send_registration_email(new_user.email, new_user.username)

        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating user: {str(e)}"
        )


async def get_user_trades(user_id: int, db: AsyncSession):
    result = await db.execute(select(models.TradeEntry).where(models.TradeEntry.user_id == user_id))
    return result.scalars().all()


@router.get('/{username}', response_model=schemas.ShowUserStocks)
async def get_user(username: str, db: AsyncSession = Depends(database.get_db)):
    """
    Get a user by username.

    Args:
        username (str): The username of the user to retrieve.
        db (AsyncSession, optional): The async database session. Defaults to Depends(database.get_db).

    Raises:
        HTTPException: If the user with the given username is not found.

    Returns:
        schemas.ShowUserStocks: The user data along with their trade entries.
    """
    try:
        result = await db.execute(select(models.User).where(models.User.username == username))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with username '{username}' not found"
            )

        # Get user trades
        trade_entries = await get_user_trades(user.user_id, db)
        trade_entries_dicts = [{key: value for key, value in entry.__dict__.items(
        ) if not key.startswith('_')} for entry in trade_entries]

        return schemas.ShowUserStocks(
            username=user.username,
            email=user.email,
            trade_entries=trade_entries_dicts
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user: {str(e)}"
        )
