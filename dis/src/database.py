"""Module for ClickHouse database operations."""

from clickhouse_driver import Client
from loguru import logger

from config import config
from models import SensorData


class ClickHouseClient:
    """Client for interacting with ClickHouse database."""

    def __init__(self):
        """Initialize the ClickHouse client."""
        self.client = Client(
            host=config.clickhouse.host,
            port=config.clickhouse.port,
            user=config.clickhouse.user,
            password=config.clickhouse.password,
            database=config.clickhouse.database,
        )
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Ensure that the sensor_data table exists."""
        try:
            # Create database if not exists
            self.client.execute(
                f"CREATE DATABASE IF NOT EXISTS {config.clickhouse.database}"
            )
            
            # Create table if not exists
            self.client.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {config.clickhouse.database}.sensor_data (
                    device_id String,
                    sensor_type String,
                    value Float64,
                    unit String,
                    timestamp DateTime,
                    location String,
                    metadata String,
                    event_date Date DEFAULT toDate(timestamp)
                ) ENGINE = MergeTree()
                PARTITION BY toYYYYMM(timestamp)
                ORDER BY (device_id, sensor_type, timestamp)
                """
            )
            logger.info("ClickHouse table check/creation completed")
        except Exception as e:
            logger.error(f"Error setting up ClickHouse table: {e}")
            raise

    def insert_sensor_data(self, sensor_data: SensorData):
        """Insert sensor data into ClickHouse.
        
        Args:
            sensor_data: The sensor data to insert
        """
        try:
            data_dict = sensor_data.to_clickhouse_dict()
            self.client.execute(
                f"""
                INSERT INTO {config.clickhouse.database}.sensor_data
                (device_id, sensor_type, value, unit, timestamp, location, metadata)
                VALUES
                """,
                [
                    (
                        data_dict["device_id"],
                        data_dict["sensor_type"],
                        data_dict["value"],
                        data_dict["unit"],
                        data_dict["timestamp"],
                        data_dict["location"],
                        data_dict["metadata"],
                    )
                ],
            )
            logger.debug(f"Inserted data for device {data_dict['device_id']}")
        except Exception as e:
            logger.error(f"Error inserting data into ClickHouse: {e}")
            raise 