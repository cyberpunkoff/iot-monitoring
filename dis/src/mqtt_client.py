"""Module for MQTT client operations."""

import json
from typing import Callable, Optional

import paho.mqtt.client as mqtt
from loguru import logger

from config import config
from models import SensorData


class MQTTClient:
    """Client for receiving data from MQTT broker."""

    def __init__(self, on_message_callback: Optional[Callable] = None):
        """Initialize the MQTT client.
        
        Args:
            on_message_callback: Callback function to process received messages
        """
        self.client = mqtt.Client(client_id=config.mqtt.client_id)
        self.on_message_callback = on_message_callback
        
        # Set up authentication if credentials are provided
        if config.mqtt.username and config.mqtt.password:
            self.client.username_pw_set(
                config.mqtt.username, 
                config.mqtt.password
            )
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def connect(self):
        """Connect to the MQTT broker and start the network loop."""
        try:
            logger.info(
                f"Connecting to MQTT broker at "
                f"{config.mqtt.broker_host}:{config.mqtt.broker_port}"
            )
            self.client.connect(
                config.mqtt.broker_host, 
                config.mqtt.broker_port
            )
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to all configured topics
            for topic in config.mqtt.topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")

    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received from the broker."""
        try:
            logger.debug(f"Received message on topic {msg.topic}")
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)
            
            # Extract device_id from the topic if not in payload
            if "device_id" not in data and "/" in msg.topic:
                topic_parts = msg.topic.split("/")
                if len(topic_parts) >= 2:
                    data["device_id"] = topic_parts[1]
            
            # Create SensorData object from the payload
            sensor_data = SensorData(**data)
            
            # Process the sensor data with callback if provided
            if self.on_message_callback:
                self.on_message_callback(sensor_data)
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in message: {payload}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        if rc != 0:
            logger.warning(
                f"Unexpected disconnection from MQTT broker, return code: {rc}"
            )
        else:
            logger.info("Disconnected from MQTT broker")

    def disconnect(self):
        """Disconnect from the MQTT broker and stop the network loop."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
            raise 