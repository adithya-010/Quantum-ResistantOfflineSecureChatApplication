# src/utils/logger.py
import logging
import sys


def setup_logger(name, level=logging.INFO):
    """Set up a logger for the application"""

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


# Test function
def test_logger():
    """Test the logger setup"""
    log = setup_logger("TEST")
    log.info("Logger test - this is working!")
    log.debug("Debug message")
    log.warning("Warning message")
    log.error("Error message")


if __name__ == "__main__":
    test_logger()