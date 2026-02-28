import sys
import os
from loguru import logger

def setup_logger():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger.remove()

    logger.add(
        sys.stderr, 
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )

    logger.add(
        "logs/game.log",
        rotation="5 MB",      
        retention="30 days",  
        compression="zip",    
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",        
        enqueue=True          
    )

    logger.info("Logging system successfully initialized!")