from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, Query, HTTPException, status, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from app.auth import authenticate_user, create_access_token, get_current_active_user, require_admin
from app.config import config
from app.database import ClickHouseClient, PostgresClient
from app.dependencies import get_db_client, get_postgres_client
from app.models import (
    SensorData, SensorDataResponse, SensorStats, SensorStatsResponse,
    UserCreate, User, Token, DeviceCreate, Device, DeviceResponse
)


app = FastAPI(
    title=config.app_name,
    description="API service for retrieving IoT sensor data from ClickHouse",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED, tags=["auth"])
async def register_user(
    user_data: UserCreate,
    db: PostgresClient = Depends(get_postgres_client)
):
    try:
        user = await db.create_user(user_data.model_dump())
        return User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in register_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering user"
        )


@app.post("/auth/token", response_model=Token, tags=["auth"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: PostgresClient = Depends(get_postgres_client)
):
    user = await authenticate_user(
        db, form_data.username, form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token_data = {
        "sub": user.username,
        "role": user.role.value
    }
    
    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer"
    }


@app.get("/auth/me", response_model=User, tags=["auth"])
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/devices", response_model=Device, status_code=status.HTTP_201_CREATED, tags=["devices"])
async def create_device(
    device_data: DeviceCreate,
    current_user: User = Depends(require_admin),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        device = await db.create_device(device_data.model_dump())
        return device
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in create_device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating device"
        )


@app.get("/devices", response_model=DeviceResponse, tags=["devices"])
async def get_devices(
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        devices = await db.get_all_devices(limit=limit)
        return DeviceResponse(data=devices, total_count=len(devices))
    except Exception as e:
        logger.error(f"Error in get_devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving devices"
        )


@app.get("/devices/{device_id}", response_model=Device, tags=["devices"])
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        device = await db.get_device(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving device"
        )


@app.put("/devices/{device_id}", response_model=Device, tags=["devices"])
async def update_device(
    device_id: str,
    device_data: dict = Body(...),
    current_user: User = Depends(require_admin),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        device = await db.update_device(device_id, device_data)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating device"
        )


@app.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["devices"])
async def delete_device(
    device_id: str,
    current_user: User = Depends(require_admin),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        success = await db.delete_device(device_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting device"
        )


@app.get("/sensor-data/latest", response_model=SensorDataResponse, tags=["sensor-data"])
async def get_latest_sensor_data(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        data = await db.get_latest_sensor_data(
            device_id=device_id,
            sensor_type=sensor_type,
            location=location,
            limit=limit
        )
        return SensorDataResponse(data=data, total_count=len(data))
    except Exception as e:
        logger.error(f"Error in get_latest_sensor_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensor-data/historical", response_model=SensorDataResponse, tags=["sensor-data"])
async def get_historical_sensor_data(
    from_timestamp: datetime,
    to_timestamp: datetime,
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = Query(default=1000, ge=1, le=10000),
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    if from_timestamp >= to_timestamp:
        raise HTTPException(
            status_code=400, 
            detail="from_timestamp must be earlier than to_timestamp"
        )
        
    try:
        data = await db.get_historical_data(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            device_id=device_id,
            sensor_type=sensor_type,
            location=location,
            limit=limit
        )
        return SensorDataResponse(data=data, total_count=len(data))
    except Exception as e:
        logger.error(f"Error in get_historical_sensor_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensor-data/stats", response_model=SensorStatsResponse, tags=["sensor-data"])
async def get_sensor_stats(
    from_timestamp: datetime,
    to_timestamp: datetime,
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    location: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    if from_timestamp >= to_timestamp:
        raise HTTPException(
            status_code=400, 
            detail="from_timestamp must be earlier than to_timestamp"
        )
        
    try:
        data = await db.get_aggregated_stats(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            device_id=device_id,
            sensor_type=sensor_type,
            location=location
        )
        return SensorStatsResponse(data=data)
    except Exception as e:
        logger.error(f"Error in get_sensor_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/devices", response_model=List[str], tags=["metadata"])
async def get_device_ids(
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        return await db.get_unique_devices()
    except Exception as e:
        logger.error(f"Error in get_device_ids: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/sensor-types", response_model=List[str], tags=["metadata"])
async def get_sensor_types(
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        return await db.get_unique_sensor_types()
    except Exception as e:
        logger.error(f"Error in get_sensor_types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/locations", response_model=List[str], tags=["metadata"])
async def get_locations(
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        return await db.get_unique_locations()
    except Exception as e:
        logger.error(f"Error in get_locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/sensor-ids", response_model=List[str], tags=["metadata"])
async def get_sensor_ids(
    current_user: User = Depends(get_current_active_user),
    db: ClickHouseClient = Depends(get_db_client)
):
    try:
        return await db.get_unique_sensor_ids()
    except Exception as e:
        logger.error(f"Error in get_sensor_ids: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
