import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt


MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = "test_publisher"
MQTT_TOPIC_TEMPLATE = "sensors/{device_id}/data"

DEVICES = [
    {"id": "device001", "type": "temperature", "unit": "°C", "location": "room1"},
    {"id": "device002", "type": "humidity", "unit": "%", "location": "room1"},
    {"id": "device003", "type": "pressure", "unit": "hPa", "location": "outside"},
    {"id": "device004", "type": "light", "unit": "lux", "location": "kitchen"},
]


def generate_random_value(device_type):
    ranges = {
        "temperature": (15.0, 35.0),
        "humidity": (30.0, 90.0),
        "pressure": (970.0, 1030.0),
        "light": (0.0, 1000.0),
    }
    min_val, max_val = ranges.get(device_type, (0.0, 100.0))
    return round(random.uniform(min_val, max_val), 2)


def create_message(device):
    return {
        "device_id": device["id"],
        "sensor_type": device["type"],
        "value": generate_random_value(device["type"]),
        "unit": device["unit"],
        "timestamp": datetime.utcnow().isoformat(),
        "location": device["location"],
        "metadata": {
            "battery": random.randint(50, 100),
            "firmware": "v1.0.3",
        },
    }


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Failed to connect to MQTT broker, return code: {rc}")


def publish_data(client):
    for device in DEVICES:
        message = create_message(device)
        topic = MQTT_TOPIC_TEMPLATE.format(device_id=device["id"])
        payload = json.dumps(message)
        result = client.publish(topic, payload)
        
        if result.rc == 0:
            print(f"Published to {topic}: {payload}")
        else:
            print(f"Failed to publish to {topic}")


def main():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        client.loop_start()
        
        try:
            while True:
                publish_data(client)
                time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping test publisher")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected from MQTT broker")


if __name__ == "__main__":
    main()
