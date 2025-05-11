"""
Data models for the Data Ingestion Service.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SensorData(BaseModel):
    """Represents data received from an IoT sensor."""
    
    device_id: str
    sensor_type: str
    value: float
    unit: str
    # timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_clickhouse_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for ClickHouse insertion."""
        return {
            "device_id": self.device_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            #"timestamp": self.timestamp,
            "location": self.location or "",
            "metadata": str(self.metadata),  # Serialize dict to string
        }

    def to_kafka_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for Kafka publishing."""
        return self.model_dump() 