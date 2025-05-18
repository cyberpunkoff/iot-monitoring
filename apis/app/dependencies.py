from app.database import ClickHouseClient, PostgresClient


clickhouse_client = ClickHouseClient()
postgres_client = PostgresClient()


async def get_db_client() -> ClickHouseClient:
    return clickhouse_client


async def get_postgres_client() -> PostgresClient:
    if not postgres_client.pool:
        await postgres_client.connect()
    return postgres_client