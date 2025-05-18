from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from clickhouse_driver import Client, defines
from loguru import logger
from passlib.context import CryptContext
import asyncpg

from app.config import config
from app.models import SensorData, SensorStats, UserInDB, UserRole, Device, User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PostgresClient:
    def __init__(self):
        self.pool = None
        logger.info("PostgreSQL client initialized")

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=config.postgres.host,
                port=config.postgres.port,
                user=config.postgres.user,
                password=config.postgres.password,
                database=config.postgres.database
            )
            logger.info(f"Connected to PostgreSQL at {config.postgres.host}:{config.postgres.port}")
            await self._ensure_tables_exist()

    async def _ensure_tables_exist(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    last_login TIMESTAMP WITH TIME ZONE,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE
                )
            """)
            logger.info("PostgreSQL tables check/creation completed")

    async def create_user(self, user_data: dict) -> UserInDB:
        username = user_data["username"]
        
        async with self.pool.acquire() as conn:
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1)",
                username
            )
            if exists:
                raise ValueError(f"User with username '{username}' already exists")
            
            now = datetime.utcnow()
            hashed_password = pwd_context.hash(user_data["password"].get_secret_value())
            
            role = user_data.get("role", UserRole.USER.value)
            
            user = {
                "username": username,
                "email": user_data["email"],
                "full_name": user_data.get("full_name", ""),
                "hashed_password": hashed_password,
                "role": role,
                "created_at": now,
                "last_login": None,
                "is_active": True
            }
            
            await conn.execute("""
                INSERT INTO users 
                (username, email, full_name, hashed_password, role, created_at, last_login, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                user["username"],
                user["email"],
                user["full_name"],
                user["hashed_password"],
                user["role"],
                user["created_at"],
                user["last_login"],
                user["is_active"]
            )
            
            return UserInDB(**user)
    
    async def get_user(self, username: str) -> Optional[UserInDB]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    username, 
                    email, 
                    full_name, 
                    hashed_password, 
                    role, 
                    created_at,
                    last_login,
                    is_active
                FROM users
                WHERE username = $1
            """, username)
            
            if not row:
                return None
                
            return UserInDB(
                username=row['username'],
                email=row['email'],
                full_name=row['full_name'],
                hashed_password=row['hashed_password'],
                role=UserRole(row['role']),
                created_at=row['created_at'],
                last_login=row['last_login'],
                is_active=row['is_active']
            )
    
    async def update_last_login(self, username: str) -> None:
        now = datetime.utcnow()
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE users 
                SET last_login = $1 
                WHERE username = $2
            """, now, username)


class ClickHouseClient:

    def __init__(self):
        self.client = Client(
            host=config.clickhouse.host,
            port=config.clickhouse.port,
            user=config.clickhouse.user,
            password=config.clickhouse.password,
            database=config.clickhouse.database,
            client_revision=defines.DBMS_MIN_PROTOCOL_VERSION_WITH_QUOTA_KEY
        )
        logger.info(f"Connected to ClickHouse at {config.clickhouse.host}:{config.clickhouse.port}")

    async def get_latest_sensor_data(
        self, 
        device_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 100
    ) -> List[SensorData]:
        query = f"""
            SELECT 
                device_id, 
                sensor_type, 
                value, 
                unit, 
                timestamp, 
                location, 
                metadata
            FROM 
                sensor_data
            WHERE 
                1=1
        """
        
        params = {}
        
        if device_id:
            query += " AND device_id = %(device_id)s"
            params["device_id"] = device_id
            
        if sensor_type:
            query += " AND sensor_type = %(sensor_type)s"
            params["sensor_type"] = sensor_type
            
        if location:
            query += " AND location = %(location)s"
            params["location"] = location
            
        query += """
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        """
        params["limit"] = limit
        
        try:
            result = self.client.execute(query, params)
            
            return [
                SensorData(
                    device_id=row[0],
                    sensor_type=row[1],
                    value=row[2],
                    unit=row[3],
                    timestamp=row[4],
                    location=row[5],
                    metadata=row[6]
                )
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error getting latest sensor data: {e}")
            raise

    async def get_historical_data(
        self,
        from_timestamp: datetime,
        to_timestamp: datetime,
        device_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 1000
    ) -> List[SensorData]:
        query = f"""
            SELECT 
                device_id, 
                sensor_type, 
                value, 
                unit, 
                timestamp, 
                location, 
                metadata
            FROM 
                sensor_data
            WHERE 
                timestamp BETWEEN %(from_ts)s AND %(to_ts)s
        """
        
        params = {
            "from_ts": from_timestamp,
            "to_ts": to_timestamp
        }
        
        if device_id:
            query += " AND device_id = %(device_id)s"
            params["device_id"] = device_id
            
        if sensor_type:
            query += " AND sensor_type = %(sensor_type)s"
            params["sensor_type"] = sensor_type
            
        if location:
            query += " AND location = %(location)s"
            params["location"] = location
            
        query += """
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        """
        params["limit"] = limit
        
        try:
            result = self.client.execute(query, params)
            
            return [
                SensorData(
                    device_id=row[0],
                    sensor_type=row[1],
                    value=row[2],
                    unit=row[3],
                    timestamp=row[4],
                    location=row[5],
                    metadata=row[6]
                )
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error getting historical sensor data: {e}")
            raise

    async def get_aggregated_stats(
        self,
        from_timestamp: datetime,
        to_timestamp: datetime,
        device_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[SensorStats]:
        query = f"""
            SELECT 
                device_id, 
                sensor_type, 
                min(value) as min_value,
                max(value) as max_value,
                avg(value) as avg_value,
                any(unit) as unit
            FROM 
                sensor_data
            WHERE 
                timestamp BETWEEN %(from_ts)s AND %(to_ts)s
        """
        
        params = {
            "from_ts": from_timestamp,
            "to_ts": to_timestamp
        }
        
        if device_id:
            query += " AND device_id = %(device_id)s"
            params["device_id"] = device_id
            
        if sensor_type:
            query += " AND sensor_type = %(sensor_type)s"
            params["sensor_type"] = sensor_type
            
        if location:
            query += " AND location = %(location)s"
            params["location"] = location
            
        query += """
            GROUP BY device_id, sensor_type
            ORDER BY device_id, sensor_type
        """
        
        try:
            result = self.client.execute(query, params)
            
            return [
                SensorStats(
                    device_id=row[0],
                    sensor_type=row[1],
                    min_value=row[2],
                    max_value=row[3],
                    avg_value=row[4],
                    unit=row[5],
                    from_timestamp=from_timestamp,
                    to_timestamp=to_timestamp
                )
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error getting aggregated sensor stats: {e}")
            raise

    async def get_unique_devices(self) -> List[str]:
        try:
            result = self.client.execute("SELECT DISTINCT device_id FROM sensor_data ORDER BY device_id")
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting unique devices: {e}")
            raise

    async def get_unique_sensor_types(self) -> List[str]:
        try:
            result = self.client.execute("SELECT DISTINCT sensor_type FROM sensor_data ORDER BY sensor_type")
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting unique sensor types: {e}")
            raise

    async def get_unique_locations(self) -> List[str]:
        try:
            result = self.client.execute("SELECT DISTINCT location FROM sensor_data ORDER BY location")
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting unique locations: {e}")
            raise

    async def get_unique_sensor_ids(self) -> List[str]:
        try:
            result = self.client.execute("SELECT DISTINCT device_id FROM sensor_data ORDER BY device_id")
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting unique sensor IDs: {e}")
            raise

    async def create_device(self, device_data: dict) -> Device:
        device_id = device_data["device_id"]

        result = self.client.execute(
            "SELECT count() FROM devices WHERE device_id = %(device_id)s",
            {"device_id": device_id}
        )
        if result[0][0] > 0:
            raise ValueError(f"Device with ID '{device_id}' already exists")
        
        now = datetime.utcnow()
        
        device = {
            "device_id": device_id,
            "name": device_data["name"],
            "location": device_data.get("location", ""),
            "description": device_data.get("description", ""),
            "created_at": now,
            "is_active": 1
        }
        
        self.client.execute(
            """
            INSERT INTO devices 
            (device_id, name, location, description, created_at, is_active)
            VALUES
            """,
            [(
                device["device_id"],
                device["name"],
                device["location"],
                device["description"],
                device["created_at"],
                device["is_active"]
            )]
        )
        
        return Device(**device)
    
    async def get_device(self, device_id: str) -> Optional[Device]:
        result = self.client.execute(
            """
            SELECT 
                device_id, 
                name, 
                location, 
                description, 
                created_at,
                is_active
            FROM devices
            WHERE device_id = %(device_id)s
            LIMIT 1
            """,
            {"device_id": device_id}
        )
        
        if not result:
            return None
            
        row = result[0]
        return Device(
            device_id=row[0],
            name=row[1],
            location=row[2],
            description=row[3],
            created_at=row[4],
            is_active=bool(row[5])
        )
    
    async def get_all_devices(self, limit: int = 100) -> List[Device]:
        result = self.client.execute(
            """
            SELECT 
                device_id, 
                name, 
                location, 
                description, 
                created_at,
                is_active
            FROM devices
            ORDER BY created_at DESC
            LIMIT %(limit)s
            """,
            {"limit": limit}
        )
        
        return [
            Device(
                device_id=row[0],
                name=row[1],
                location=row[2],
                description=row[3],
                created_at=row[4],
                is_active=bool(row[5])
            )
            for row in result
        ]
    
    async def update_device(self, device_id: str, device_data: dict) -> Optional[Device]:
        device = await self.get_device(device_id)
        if not device:
            return None

        update_parts = []
        params = {"device_id": device_id}
        
        if "name" in device_data:
            update_parts.append("name = %(name)s")
            params["name"] = device_data["name"]
            
        if "location" in device_data:
            update_parts.append("location = %(location)s")
            params["location"] = device_data["location"]
            
        if "description" in device_data:
            update_parts.append("description = %(description)s")
            params["description"] = device_data["description"]
            
        if "is_active" in device_data:
            update_parts.append("is_active = %(is_active)s")
            params["is_active"] = 1 if device_data["is_active"] else 0
        
        if update_parts:
            update_query = f"ALTER TABLE devices UPDATE {', '.join(update_parts)} WHERE device_id = %(device_id)s"
            self.client.execute(update_query, params)

        return await self.get_device(device_id)
        
    async def delete_device(self, device_id: str) -> bool:
        device = await self.get_device(device_id)
        if not device:
            return False

        self.client.execute(
            "ALTER TABLE devices DELETE WHERE device_id = %(device_id)s",
            {"device_id": device_id}
        )
        
        return True
