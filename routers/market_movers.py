from operator import index
import oauth2
import asyncio
import schemas
from fastapi import APIRouter, Depends, HTTPException, Response, status
from utils import market_movers_utils

router = APIRouter(
    prefix="/market_movers",
    tags=["market_movers"]
)


@router.get("/main_indices")
async def get_main_indices(current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Get main market indices.

    This endpoint fetches the main market indices and returns them in a dictionary.
    The current authenticated user is passed as a parameter, but is not used in the function.

    Parameters:
    - current_user: The current authenticated user.

    Returns:
    - A dictionary containing the main market indices.

    Example:
    {
        "NIFTY 50": {"value": 17300.15, "change": -29.20, "change_percent": -0.17},
        "INDIA VIX": {"value": 20.5875, "change": 0.20, "change_percent": 0.98},
        "NIFTY BANK": {"value": 36552.00, "change": -112.20, "change_percent": -0.31}
    }
    """
    try:
        # Fetch the main market indices
        indices_info = await market_movers_utils.fetch_main_indices()
    except Exception as e:
        # If an exception occurs during fetching, raise an HTTPException
        raise HTTPException(
            status_code=500, detail="Failed to fetch market indices") from e

    # Return the fetched indices
    return indices_info
