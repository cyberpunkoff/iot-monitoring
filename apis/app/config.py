"""Configuration settings for the API service."""

import os
from datetime import timedelta
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ClickHouseSettings(BaseModel):
    """ClickHouse database settings."""
    host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    port: int = int(os.getenv("CLICKHOUSE_PORT", "9000"))
    user: str = os.getenv("CLICKHOUSE_USER", "default")
    password: str = os.getenv("CLICKHOUSE_PASSWORD", "")
    database: str = os.getenv("CLICKHOUSE_DATABASE", "default")


class JWTSettings(BaseModel):
    """JWT authentication settings."""
    secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt-please-change-in-production")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    @property
    def access_token_expires(self) -> timedelta:
        """Get the access token expiration time as a timedelta."""
        return timedelta(minutes=self.access_token_expire_minutes)


class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "IoT Monitoring API Service"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    clickhouse: ClickHouseSettings = ClickHouseSettings()
    jwt: JWTSettings = JWTSettings()


# Create a global config instance
config = Settings() 