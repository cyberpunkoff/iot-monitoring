"""Module for FastAPI dependencies."""

from app.database import ClickHouseClient


# Database client instance that will be used as a dependency
db_client = ClickHouseClient()


def get_db_client() -> ClickHouseClient:
    """Dependency to get the database client.
    
    Returns:
        A ClickHouseClient instance
    """
    return db_client 