import os
from datetime import timedelta
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class ClickHouseSettings(BaseModel):
    host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    port: int = int(os.getenv("CLICKHOUSE_PORT", "9000"))
    user: str = os.getenv("CLICKHOUSE_USER", "default")
    password: str = os.getenv("CLICKHOUSE_PASSWORD", "")
    database: str = os.getenv("CLICKHOUSE_DATABASE", "default")


class PostgresSettings(BaseModel):
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    database: str = os.getenv("POSTGRES_DATABASE", "iot_monitoring")


class JWTSettings(BaseModel):
    secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt-please-change-in-production")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    @property
    def access_token_expires(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)


class Settings(BaseSettings):
    app_name: str = "IoT Monitoring API Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    clickhouse: ClickHouseSettings = ClickHouseSettings()
    postgres: PostgresSettings = PostgresSettings()
    jwt: JWTSettings = JWTSettings()


config = Settings()
