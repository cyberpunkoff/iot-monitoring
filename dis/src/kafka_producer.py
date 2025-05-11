"""Module for Kafka producer operations."""

import json
from kafka import KafkaProducer
from loguru import logger

from config import config
from models import SensorData


class SensorDataProducer:
    """Producer for sending sensor data to Kafka."""

    def __init__(self):
        """Initialize the Kafka producer."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=config.kafka.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            logger.info(
                f"Kafka producer initialized with servers: "
                f"{config.kafka.bootstrap_servers}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

    def send_sensor_data(self, sensor_data: SensorData):
        """Send sensor data to Kafka topic.
        
        Args:
            sensor_data: The sensor data to send
        """
        try:
            future = self.producer.send(
                config.kafka.topic, 
                sensor_data.to_kafka_dict()
            )
            # Wait for message to be sent
            future.get(timeout=10)
            logger.debug(
                f"Sent data to Kafka topic {config.kafka.topic} "
                f"for device {sensor_data.device_id}"
            )
        except Exception as e:
            logger.error(f"Error sending data to Kafka: {e}")
            raise

    def close(self):
        """Close the Kafka producer."""
        if hasattr(self, "producer"):
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed") 