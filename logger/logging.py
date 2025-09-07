import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

load_dotenv()

LOGGER_NAME = os.getenv("APPLICATION_NAME")
LOG_FILE_PATH = "/app/logs"
MAX_BYTES = 5 * 1024 * 1024  # Maximum log file size before rotation (5 MB)
BACKUP_COUNT = 5             # Number of backup log files to keep


def get_logger() -> logging.Logger:
    """
    Creates and returns an application-wide logger.

    This logger uses a RotatingFileHandler to manage log files efficiently.
    When the log file reaches MAX_BYTES in size, it is rotated, and older
    files are renamed and kept up to BACKUP_COUNT copies.

    Returns
    -------
    logging.Logger
        Configured logger instance with a rotating file handler.

    Notes
    -----
    - The log directory is created if it does not exist.
    - Log format includes timestamp, log level, logger name, and the message.
    - Logging level is set to DEBUG (captures all logs).
    - Multiple calls to `get_logger()` return the same logger instance
      (avoids duplicate handlers).
    """

    # Ensure log directory exists (creates if missing)
    os.makedirs(LOG_FILE_PATH, exist_ok=True)

    # Construct the log file path
    log_file = os.path.join(LOG_FILE_PATH, "app.log")

    # Create or fetch the logger instance by name
    logger_name = LOGGER_NAME
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Capture DEBUG and above levels

    # Avoid adding multiple handlers if logger already configured
    if not logger.handlers:
        handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        # Define log format
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Attach the handler to the logger
        logger.addHandler(handler)

    return logger