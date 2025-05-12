import uvicorn
from loguru import logger

from app.config import config


if __name__ == "__main__":
    logger.info(f"Starting {config.app_name}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug
    )
