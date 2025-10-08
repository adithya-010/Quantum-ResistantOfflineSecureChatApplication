import logging
import colorlog
from datetime import datetime

def get_logger(name="APP"):
    log_format = (
        "%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]%(reset)s %(message)s"
    )
    colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(log_format, log_colors=colors))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Optional file logging
        file_handler = logging.FileHandler(f"logs_{datetime.now().date()}.log")
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)

    return logger
