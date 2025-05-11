"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

from app.config import config
from app.database import ClickHouseClient
from app.dependencies import get_db_client
from app.models import TokenData, UserInDB, User, UserRole


# Password verification context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time, defaults to 30 minutes
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + config.jwt.access_token_expires
        
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode, 
        config.jwt.secret_key, 
        algorithm=config.jwt.algorithm
    )


async def authenticate_user(
    db: ClickHouseClient, username: str, password: str
) -> Union[UserInDB, bool]:
    """Authenticate a user with username and password.
    
    Args:
        db: Database client
        username: Username to authenticate
        password: Password to verify
        
    Returns:
        UserInDB object if authentication succeeds, False otherwise
    """
    user = await db.get_user(username)
    
    if not user:
        return False
        
    if not verify_password(password, user.hashed_password):
        return False
        
    # Update last login time
    await db.update_last_login(username)
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: ClickHouseClient = Depends(get_db_client)
) -> User:
    """Get the current authenticated user from JWT token.
    
    Args:
        token: JWT token from OAuth2 scheme
        db: Database client
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            config.jwt.secret_key, 
            algorithms=[config.jwt.algorithm]
        )
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role is None:
            logger.warning("Missing username or role in token")
            raise credentials_exception
            
        token_data = TokenData(username=username, role=UserRole(role))
        
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise credentials_exception
    
    user = await db.get_user(token_data.username)
    
    if user is None:
        logger.warning(f"User not found: {token_data.username}")
        raise credentials_exception
        
    if not user.is_active:
        logger.warning(f"Inactive user: {token_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=user.created_at,
        is_active=user.is_active
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if current user has admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
