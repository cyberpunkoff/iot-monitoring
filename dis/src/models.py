from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SensorData(BaseModel):
    device_id: str
    sensor_type: str
    value: float
    unit: str
    # timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_clickhouse_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            #"timestamp": self.timestamp,
            "location": self.location or "",
            "metadata": str(self.metadata),
        }

    def to_kafka_dict(self) -> Dict[str, Any]:
        return self.model_dump()
