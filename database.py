from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# MySQL Database Configuration
MYSQL_USER = 'sqluser'
MYSQL_PASSWORD = 'password'
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'
MYSQL_DATABASE = 'stock_tracker_app'

Base = declarative_base()


# Create MySQL Database URL
SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{MYSQL_USER}:{
    MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create a SQLAlchemy engine that provides a source of connectivity to the database
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker that will generate new Session objects when called
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    """
    Get a database session.

    This function creates a new SQLAlchemy session, yields it for use in a route, and then closes it after the route is done.
    It's a generator function that can be used in FastAPI routes with the Depends function to inject a SQLAlchemy session into a route.
    """
    async with async_session() as session:
        yield session
