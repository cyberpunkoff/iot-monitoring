import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class MQTTConfig(BaseModel):
    broker_host: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    broker_port: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    client_id: str = os.getenv("MQTT_CLIENT_ID", "data_ingestion_service")
    username: str = os.getenv("MQTT_USERNAME", "")
    password: str = os.getenv("MQTT_PASSWORD", "")
    topics: list[str] = os.getenv("MQTT_TOPICS", "sensors/+/data").split(",")

class ClickHouseConfig(BaseModel):
    host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    port: int = int(os.getenv("CLICKHOUSE_PORT", "9000"))
    user: str = os.getenv("CLICKHOUSE_USER", "default")
    password: str = os.getenv("CLICKHOUSE_PASSWORD", "")
    database: str = os.getenv("CLICKHOUSE_DATABASE", "iot_monitoring")

class Config(BaseModel):
    mqtt: MQTTConfig = MQTTConfig()
    clickhouse: ClickHouseConfig = ClickHouseConfig()
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

config = Config() 