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
    _file_handler = None  # Shared file handler across all loggers
    _pytest_handler = None  # Shared pytest.log handler

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

        # Prevent propagation to root logger to avoid duplicates with pytest
        logger.propagate = False

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s',
            datefmt='%H:%M:%S'
        )

        # Create shared file handlers if they don't exist (one per test session)
        if TestLogger._file_handler is None:
            # Timestamped log file for this test run
            log_file = config.LOGS_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            TestLogger._file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
            TestLogger._file_handler.setLevel(logging.DEBUG)
            TestLogger._file_handler.setFormatter(detailed_formatter)

            # Also write to main pytest.log for convenience
            pytest_log = config.LOGS_DIR / "latest_test_run.log"
            TestLogger._pytest_handler = logging.FileHandler(pytest_log, encoding='utf-8', mode='w')
            TestLogger._pytest_handler.setLevel(logging.DEBUG)
            TestLogger._pytest_handler.setFormatter(detailed_formatter)

        # Console handler (per logger, but will show same info)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)

        # Add handlers
        logger.addHandler(TestLogger._file_handler)
        logger.addHandler(TestLogger._pytest_handler)
        logger.addHandler(console_handler)

        TestLogger._loggers[name] = logger

        return logger

    @staticmethod
    def reset_loggers():
        """Reset all loggers (useful for testing or new test sessions)"""
        for logger in TestLogger._loggers.values():
            logger.handlers.clear()
        TestLogger._loggers.clear()
        if TestLogger._file_handler:
            TestLogger._file_handler.close()
        if TestLogger._pytest_handler:
            TestLogger._pytest_handler.close()
        TestLogger._file_handler = None
        TestLogger._pytest_handler = None


# Convenience function
def get_logger(name: str = "test_automation") -> logging.Logger:
    """Get logger instance"""
    return TestLogger.get_logger(name)