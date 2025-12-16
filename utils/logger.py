"""
Logging utility for the test automation framework
Provides structured logging with file and console output
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config.config import get_config


class TestLogger:
    """Custom logger for test automation"""

    _loggers = {}

    @staticmethod
    def get_logger(name: str = "test_automation") -> logging.Logger:
        """
        Get or create a logger instance

        Args:
            name: Logger name

        Returns:
            Configured logger instance
        """
        if name in TestLogger._loggers:
            return TestLogger._loggers[name]

        config = get_config()
        config.create_directories()

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # File handler (detailed logs)
        log_file = config.LOGS_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        # Console handler (simplified logs)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        TestLogger._loggers[name] = logger

        return logger


# Convenience function
def get_logger(name: str = "test_automation") -> logging.Logger:
    """Get logger instance"""
    return TestLogger.get_logger(name)