import signal
import sys
import time
from loguru import logger

from config import config
from database import ClickHouseClient
from kafka_producer import SensorDataProducer
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
        self.kafka_producer = SensorDataProducer()
        self.mqtt_client = MQTTClient(on_message_callback=self.process_sensor_data)
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def start(self):
        logger.info("Starting Data Ingestion Service")
        self.mqtt_client.connect()
        logger.info("Service started and listening for messages")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def process_sensor_data(self, sensor_data: SensorData):
        try:
            self.clickhouse_client.insert_sensor_data(sensor_data)
            
            self.kafka_producer.send_sensor_data(sensor_data)
            
            logger.info(
                f"Processed data from device {sensor_data.device_id}, "
                f"sensor {sensor_data.sensor_type}"
            )
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")

    def shutdown(self):
        logger.info("Shutting down Data Ingestion Service")
        self.mqtt_client.disconnect()
        self.kafka_producer.close()
        logger.info("Service shut down completed")

    def signal_handler(self, sig, frame):
        logger.info(f"Received signal {sig}, shutting down")
        self.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    service = DataIngestionService()
    service.start()
