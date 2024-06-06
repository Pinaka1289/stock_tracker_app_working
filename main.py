from starlette.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
import models
import database
from routers import stocks, user, authentication, market_movers
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5174",  # Vite development server
    "http://localhost:5173",  # Vite development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


async def create_tables():
    """
    Asynchronously create database tables.

    This function creates the database tables defined in the models asynchronously.

    Returns:
        None
    """
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("startup")
async def startup_event():
    """
    Event handler to create tables on application startup.

    This event handler triggers the creation of database tables on application startup.

    Returns:
        None
    """
    await create_tables()

# Include routers
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(stocks.router)
app.include_router(market_movers.router)
