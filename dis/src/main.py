import sys
import time
from loguru import logger

from config import config
from database import ClickHouseClient
from mqtt_client import MQTTClient
from models import SensorData


class DataIngestionService:

    def __init__(self):
        logger.remove()
        logger.add(
            sys.stderr,
            level=config.log_level,
            format="{time} | {level} | {message}"
        )
        
        logger.info("Initializing Data Ingestion Service")
        
        self.clickhouse_client = ClickHouseClient()
        self.mqtt_client = MQTTClient(on_message_callback=self.process_sensor_data)

    def start(self):
        logger.info("Starting Data Ingestion Service")
        self.mqtt_client.connect()
        logger.info("Service started and listening for messages")
        
        while True:
            time.sleep(1)

    def process_sensor_data(self, sensor_data: SensorData):
        try:
            self.clickhouse_client.insert_sensor_data(sensor_data)
            
            logger.info(
                f"Processed data from device {sensor_data.device_id}, "
                f"sensor {sensor_data.sensor_type}"
            )
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")


if __name__ == "__main__":
    service = DataIngestionService()
    service.start()
