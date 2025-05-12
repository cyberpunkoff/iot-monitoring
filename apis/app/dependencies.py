from app.database import ClickHouseClient


db_client = ClickHouseClient()


def get_db_client() -> ClickHouseClient:
    return db_client