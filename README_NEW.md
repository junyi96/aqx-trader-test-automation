# AQX Trader Test Automation Framework

A professional, production-ready test automation framework for AQX Trader application using Playwright and Python with Page Object Model design pattern.

## Table of Contents

- [Overview](#overview)
- [Framework Architecture](#framework-architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Writing New Tests](#writing-new-tests)
- [CI/CD Integration](#cicd-integration)
- [Reporting](#reporting)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

This framework provides a scalable, maintainable solution for automated testing of the AQX Trader platform. It implements industry-standard design patterns and best practices for test automation.

### Key Technologies

- **Python 3.9+**: Programming language
- **Playwright**: Browser automation
- **Pytest**: Test framework
- **Page Object Model**: Design pattern for maintainability
- **GitHub Actions**: CI/CD pipeline

## Framework Architecture

### Design Patterns

1. **Page Object Model (POM)**: Separates page interactions from test logic
2. **Factory Pattern**: Generates test data dynamically
3. **Fixture Pattern**: Manages test setup and teardown
4. **Configuration Management**: Environment-specific settings

### Architecture Diagram

```
aqx-trader-test-automation/
├── config/              # Configuration management
├── pages/               # Page Object Model classes
├── tests/               # Test cases organized by feature
├── utils/               # Utility functions and helpers
├── test_data/           # Test data files
├── reports/             # Test execution reports
├── screenshots/         # Screenshots on failure
├── traces/              # Playwright traces
└── logs/                # Application logs
```

## Features

### Core Features

- ✅ **Page Object Model**: Clean separation of concerns
- ✅ **Data-Driven Testing**: Parameterized tests with multiple data sets
- ✅ **Logging**: Comprehensive logging with file and console output
- ✅ **Reporting**: HTML reports with screenshots and traces
- ✅ **CI/CD Ready**: GitHub Actions workflow included
- ✅ **Docker Support**: Containerized test execution
- ✅ **Multi-Browser**: Support for Chromium, Firefox, and WebKit
- ✅ **Retry Logic**: Automatic retry for flaky tests
- ✅ **Custom Waits**: Smart waiting strategies
- ✅ **Screenshot on Failure**: Automatic capture on test failure
- ✅ **Trace Recording**: Full Playwright traces for debugging

### Test Coverage

- Market Orders (with Stop Loss and Take Profit)
- Limit Orders (all expiry types)
- Stop Orders (all expiry types)
- Position Management (edit, partial close, full close)
- Pending Order Management
- Order History Validation

## Project Structure

```
aqx-trader-test-automation/
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI pipeline
│
├── config/
│   ├── __init__.py
│   └── config.py                     # Configuration management
│
├── pages/                            # Page Object Model
│   ├── __init__.py
│   ├── base_page.py                  # Base page class
│   ├── login_page.py                 # Login functionality
│   ├── trading_page.py               # Trading operations
│   └── assets_page.py                # Asset management
│
├── tests/                            # Test cases
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures and configuration
│   ├── test_market_orders.py         # Market order tests
│   ├── test_limit_orders.py          # Limit order tests
│   ├── test_stop_orders.py           # Stop order tests
│   └── test_position_management.py   # Position management tests
│
├── utils/                            # Utilities
│   ├── __init__.py
│   ├── logger.py                     # Logging utility
│   ├── data_helpers.py               # Test data generators
│   └── custom_waits.py               # Custom wait conditions
│
├── test_data/
│   └── order_types.json              # Test data definitions
│
├── reports/                          # Test reports (generated)
├── screenshots/                      # Screenshots (generated)
├── traces/                           # Playwright traces (generated)
├── logs/                             # Log files (generated)
│
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── Dockerfile                        # Docker configuration
├── docker-compose.yml                # Docker Compose configuration
├── pytest.ini                        # Pytest configuration
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd aqx-trader-test-automation
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers

```bash
playwright install
```

### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Never commit .env file to version control!
```

## Configuration

### Environment Variables

Edit `.env` file:

```bash
TEST_ENV=development          # development, staging, production
AQX_USERNAME=your_username
AQX_PASSWORD=your_password
BROWSER=chromium             # chromium, firefox, webkit
HEADLESS=false               # true for headless mode
SLOW_MO=0                    # milliseconds delay for debugging
```

### Configuration Files

- `config/config.py`: Main configuration
- `pytest.ini`: Pytest settings
- `test_data/order_types.json`: Test data

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_market_orders.py
```

### Run Tests by Marker

```bash
# Run only smoke tests
pytest -m smoke

# Run only market order tests
pytest -m market_order

# Run limit and stop order tests
pytest -m "limit_order or stop_order"
```

### Run with HTML Report

```bash
pytest --html=reports/report.html --self-contained-html
```

### Run in Headless Mode

```bash
HEADLESS=true pytest
```

### Run in Parallel (requires pytest-xdist)

```bash
pytest -n auto
```

### Run Specific Test

```bash
pytest tests/test_market_orders.py::TestMarketOrders::test_create_market_order_with_stop_loss_and_take_profit
```

### Docker Execution

```bash
# Build and run
docker-compose up test-runner

# Run with parallel execution
docker-compose up test-runner-parallel
```

## Writing New Tests

### Example Test

```python
import pytest
from pages.trading_page import TradingPage
from utils.logger import get_logger
from utils.data_helpers import OrderDataGenerator

logger = get_logger(__name__)

@pytest.mark.market_order
@pytest.mark.smoke
class TestMyFeature:

    def test_my_new_feature(self, trading_page: TradingPage):
        """Test description"""
        logger.info("Starting my test")

        # Use page objects
        current_price = trading_page.get_current_buy_price()

        # Use data helpers
        order_data = OrderDataGenerator.generate_market_order_data(current_price)

        # Perform actions
        trading_page.place_market_order(**order_data)

        # Assertions
        assert True, "Test assertion message"

        logger.info("Test completed successfully")
```

### Adding a New Page Object

```python
from pages.base_page import BasePage
from playwright.sync_api import Page

class MyNewPage(BasePage):

    # Locators
    ELEMENT_ID = "test-id"

    def __init__(self, page: Page):
        super().__init__(page)

    def perform_action(self):
        """Action description"""
        self.get_by_test_id(self.ELEMENT_ID).click()
```

## CI/CD Integration

### GitHub Actions

The framework includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

- Runs on push to main/develop branches
- Runs on pull requests
- Scheduled daily runs at 2 AM UTC
- Tests against multiple Python versions and browsers
- Generates and uploads test reports
- Uploads screenshots and traces on failure

### Required Secrets

Add these secrets to your GitHub repository:

- `AQX_USERNAME`: Test account username
- `AQX_PASSWORD`: Test account password

## Reporting

### HTML Reports

Generated in `reports/` directory after test execution.

View with:
```bash
# Windows
start reports/report.html

# macOS
open reports/report.html

# Linux
xdg-open reports/report.html
```

### Playwright Traces

Traces are saved in `traces/` directory.

View with:
```bash
playwright show-trace traces/trace.zip
```

### Logs

Detailed logs in `logs/` directory:
- Console output (INFO level)
- File output (DEBUG level)
- Timestamped log files per test run

## Best Practices

### 1. Use Page Objects

❌ **Don't:**
```python
def test_bad():
    page.locator("#username").fill("user")
    page.locator("#password").fill("pass")
```

✅ **Do:**
```python
def test_good(login_page: LoginPage):
    login_page.enter_username("user")
    login_page.enter_password("pass")
```

### 2. Use Data Helpers

❌ **Don't:**
```python
def test_bad():
    stop_loss = current_price * 0.95
```

✅ **Do:**
```python
def test_good():
    stop_loss = OrderDataGenerator.calculate_stop_loss(current_price)
```

### 3. Use Logging

```python
from utils.logger import get_logger

logger = get_logger(__name__)

def test_example():
    logger.info("Starting test")
    logger.debug(f"Current value: {value}")
    logger.error("Something went wrong")
```

### 4. Use Markers

```python
@pytest.mark.smoke
@pytest.mark.market_order
def test_critical_feature():
    pass
```

### 5. Write Descriptive Test Names

❌ **Don't:** `def test_1():`

✅ **Do:** `def test_create_market_order_with_stop_loss_and_take_profit():`

## Troubleshooting

### Tests Failing Due to Timeout

Increase timeout in `config/config.py`:
```python
DEFAULT_TIMEOUT = 60000  # 60 seconds
```

### Browser Not Launching

Reinstall browsers:
```bash
playwright install --force
```

### Import Errors

Ensure you're in the project root and virtual environment is activated:
```bash
cd aqx-trader-test-automation
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### View Detailed Logs

Check log files in `logs/` directory for detailed debugging information.

### Debug with Trace Viewer

```bash
playwright show-trace traces/trace.zip
```

## Contributing

1. Create a feature branch
2. Write tests following the framework patterns
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

## License

[Your License Here]

## Contact

[Your Contact Information]

---

**Built with best practices for production-ready test automation**