# src/utils/logger.py
import logging
import colorlog

def get_logger(name="QuantumSecureChat"):
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent adding multiple handlers if called multiple times
    if not logger.handlers:
        # Create console handler with color
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(levelname)s]%(reset)s %(name)s: %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
