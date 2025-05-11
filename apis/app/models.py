"""Data models for the API service."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, EmailStr, SecretStr


class SensorData(BaseModel):
    """Model representing sensor data."""
    device_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    location: str
    metadata: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "device-001",
                "sensor_type": "temperature",
                "value": 23.5,
                "unit": "celsius",
                "timestamp": "2023-08-15T13:45:30",
                "location": "room-123",
                "metadata": '{"humidity": 65, "battery": 89}'
            }
        }


class SensorDataResponse(BaseModel):
    """Model for returning sensor data in API responses."""
    data: List[SensorData]
    total_count: int


class SensorStats(BaseModel):
    """Model for aggregated sensor statistics."""
    device_id: str
    sensor_type: str
    min_value: float
    max_value: float
    avg_value: float
    unit: str
    from_timestamp: datetime
    to_timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "device-001",
                "sensor_type": "temperature",
                "min_value": 19.5,
                "max_value": 26.8,
                "avg_value": 22.7,
                "unit": "celsius",
                "from_timestamp": "2023-08-15T00:00:00",
                "to_timestamp": "2023-08-15T23:59:59"
            }
        }


class SensorStatsResponse(BaseModel):
    """Model for returning sensor statistics in API responses."""
    data: List[SensorStats]


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base model for user data."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for user creation with password."""
    password: SecretStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "password": "securepassword123"
            }
        }


class UserInDB(UserBase):
    """Model for user data stored in database."""
    hashed_password: str
    role: UserRole = UserRole.USER
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True


class User(UserBase):
    """Model for user data returned in API responses."""
    role: UserRole
    created_at: datetime
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role": "user",
                "created_at": "2023-08-15T13:45:30",
                "is_active": True
            }
        }


class Token(BaseModel):
    """Model for token response."""
    access_token: str
    token_type: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Model for token payload data."""
    username: str
    role: UserRole


class DeviceBase(BaseModel):
    """Base model for device data."""
    device_id: str
    name: str
    location: Optional[str] = None
    description: Optional[str] = None


class DeviceCreate(DeviceBase):
    """Model for device creation."""
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "device-001",
                "name": "Temperature Sensor 1",
                "location": "room-123",
                "description": "Main temperature sensor for Room 123"
            }
        }


class Device(DeviceBase):
    """Model for device data returned in API responses."""
    created_at: datetime
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "device-001",
                "name": "Temperature Sensor 1",
                "location": "room-123",
                "description": "Main temperature sensor for Room 123",
                "created_at": "2023-08-15T13:45:30",
                "is_active": True
            }
        }


class DeviceResponse(BaseModel):
    """Model for returning devices in API responses."""
    data: List[Device]
    total_count: int
