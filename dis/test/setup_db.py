"""
ClickHouse database setup script.

This script creates the necessary database and tables for the Data Ingestion Service.
"""

from clickhouse_driver import Client
from loguru import logger
import sys

from config import config


def setup_database():
    """Set up the ClickHouse database and tables."""
    logger.info(f"Setting up ClickHouse database: {config.clickhouse.database}")
    
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level=config.log_level)
    
    try:
        # Connect to ClickHouse
        client = Client(
            host=config.clickhouse.host,
            port=config.clickhouse.port,
            user=config.clickhouse.user,
            password=config.clickhouse.password,
        )
        
        # Create database if not exists
        client.execute(
            f"CREATE DATABASE IF NOT EXISTS {config.clickhouse.database}"
        )
        logger.info(f"Database '{config.clickhouse.database}' created or already exists")
        
        # Create sensor_data table
        client.execute(
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
        logger.info("Table 'sensor_data' created or already exists")
        
        # Create a summary table with materialized view
        client.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {config.clickhouse.database}.sensor_data_summary (
                device_id String,
                sensor_type String,
                date Date,
                min_value Float64,
                max_value Float64,
                avg_value Float64,
                count UInt64
            ) ENGINE = SummingMergeTree()
            ORDER BY (device_id, sensor_type, date)
            """
        )
        logger.info("Table 'sensor_data_summary' created or already exists")
        
        # Create materialized view if not exists
        client.execute(
            f"""
            CREATE MATERIALIZED VIEW IF NOT EXISTS {config.clickhouse.database}.sensor_data_summary_mv
            TO {config.clickhouse.database}.sensor_data_summary
            AS
            SELECT
                device_id,
                sensor_type,
                toDate(timestamp) as date,
                min(value) as min_value,
                max(value) as max_value,
                avg(value) as avg_value,
                count() as count
            FROM {config.clickhouse.database}.sensor_data
            GROUP BY device_id, sensor_type, date
            """
        )
        logger.info("Materialized view 'sensor_data_summary_mv' created or already exists")
        
        client.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username String,
                    email String,
                    full_name String,
                    hashed_password String,
                    role String,
                    created_at DateTime,
                    last_login Nullable(DateTime),
                    is_active UInt8
                )
                ENGINE = MergeTree()
                ORDER BY (username)
                PRIMARY KEY (username)
            """)
            
        # Create devices table if it doesn't exist
        client.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id String,
                name String,
                location String,
                description String,
                created_at DateTime,
                is_active UInt8
            )
            ENGINE = MergeTree()
            ORDER BY (device_id)
            PRIMARY KEY (device_id)
        """)

        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise


if __name__ == "__main__":
    setup_database() 