"""
Configuration management for the test automation framework.
Handles environment-specific settings and test data.
"""
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Base configuration class"""

    # Project paths
    ROOT_DIR = Path(__file__).parent.parent
    CONFIG_DIR = ROOT_DIR / "config"
    TEST_DATA_DIR = ROOT_DIR / "test_data"
    REPORTS_DIR = ROOT_DIR / "reports"
    SCREENSHOTS_DIR = ROOT_DIR / "screenshots"
    LOGS_DIR = ROOT_DIR / "logs"
    TRACES_DIR = ROOT_DIR / "traces"

    # Browser settings
    BROWSER = os.getenv("BROWSER", "chromium")
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    SLOW_MO = int(os.getenv("SLOW_MO", "0"))

    # Timeout settings (in milliseconds)
    DEFAULT_TIMEOUT = 30000
    NAVIGATION_TIMEOUT = 30000
    ACTION_TIMEOUT = 10000

    # Test settings
    TAKE_SCREENSHOT_ON_FAILURE = True
    SAVE_TRACE_ON_FAILURE = True

    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1000  # milliseconds

    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        for dir_path in [cls.REPORTS_DIR, cls.SCREENSHOTS_DIR, cls.LOGS_DIR, cls.TRACES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment configuration"""
    BASE_URL = "https://aqxtrader.aquariux.com"
    ENV = "development"

    # Credentials - Should be loaded from environment variables
    USERNAME = os.getenv("AQX_USERNAME", "1000370")
    PASSWORD = os.getenv("AQX_PASSWORD", "FE4Pi$q5Syj$")


class StagingConfig(Config):
    """Staging environment configuration"""
    BASE_URL = os.getenv("STAGING_URL", "https://staging.aqxtrader.aquariux.com")
    ENV = "staging"

    USERNAME = os.getenv("AQX_USERNAME")
    PASSWORD = os.getenv("AQX_PASSWORD")


class ProductionConfig(Config):
    """Production environment configuration"""
    BASE_URL = os.getenv("PROD_URL", "https://aqxtrader.aquariux.com")
    ENV = "production"

    USERNAME = os.getenv("AQX_USERNAME")
    PASSWORD = os.getenv("AQX_PASSWORD")


# Configuration mapping
config_map: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}


def get_config() -> Config:
    """
    Get configuration based on environment variable.
    Defaults to development if not specified.
    """
    env = os.getenv("TEST_ENV", "development").lower()
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()