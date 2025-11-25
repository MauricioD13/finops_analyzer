import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def get_logger():
    """Get the singleton logger instance with file rotation"""
    # Get logs directory from environment variable, default to ./logs
    logs_dir = os.getenv("LOGS_DIR", "./logs")

    # Create logs directory if it doesn't exist
    Path(logs_dir).mkdir(parents=True, exist_ok=True)

    # Configure logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # Format for logs
    formatter = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler (10MB per file, keep 5 backup files)
    log_file = os.path.join(logs_dir, "app.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = get_logger()