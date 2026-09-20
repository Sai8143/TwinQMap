import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Dict

# Define directory for log files
LOGS_DIR = r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map\logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Standard logging formatter
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)

# Keep track of initialized loggers to avoid multiple handlers
_loggers: Dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves or creates a named logger that outputs logs to both
    the console and a specialized log file inside logs/.
    
    Args:
        name: Name of the logger (e.g., 'digital_twin', 'scheduler', 'prediction')
        
    Returns:
        A configured logging.Logger instance.
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Prevent duplicating handlers if they already exist
    if not logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # File Handler (Rotating, max 10MB per file, keeping 5 backups)
        log_file_path = os.path.join(LOGS_DIR, f"{name}.log")
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger

# Pre-defined specialized loggers for different modules
prediction_logger = get_logger("prediction")
execution_logger = get_logger("execution")
scheduler_logger = get_logger("scheduler")
digital_twin_logger = get_logger("digital_twin")
mongodb_logger = get_logger("database")
training_logger = get_logger("training")
quantum_api_logger = get_logger("quantum_api")
general_logger = get_logger("general")
