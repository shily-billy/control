"""Logging configuration"""
from loguru import logger
import sys

def setup_logger(name: str = None):
    """Setup and configure logger"""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Add file handler
    logger.add(
        "logs/control_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG"
    )
    
    return logger
