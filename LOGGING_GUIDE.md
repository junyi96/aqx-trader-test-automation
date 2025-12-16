# Logging Guide for AQX Trader Test Automation Framework

## Overview

The framework provides comprehensive logging at multiple levels to help with debugging, monitoring, and test analysis.

## Logging System

### Two Logging Mechanisms

1. **Custom Logger** (`utils/logger.py`)
   - Application-level logging
   - Controlled by your code
   - Used in tests and page objects

2. **Pytest Logging** (built-in)
   - Framework-level logging
   - Captures pytest output
   - Configured in `pytest.ini`

## Log Files Created

After running tests, you'll find these log files in the `logs/` directory:

```
logs/
├── test_run_20241216_143022.log    # Timestamped run (from custom logger)
├── latest_test_run.log             # Latest run (always overwritten)
└── pytest.log                      # Pytest's built-in logging
```

### 1. Timestamped Log (test_run_YYYYMMDD_HHMMSS.log)

**Purpose**: Permanent record of each test execution

**Contains**:
- All DEBUG and INFO level messages from your tests
- Detailed method calls from page objects
- Test execution flow
- Variable values
- Assertions

**Example**:
```
2024-12-16 14:30:22 - tests.test_market_orders - [INFO] - test_market_orders.py:35 - Starting test: Create market order with SL and TP
2024-12-16 14:30:23 - tests.test_market_orders - [INFO] - test_market_orders.py:39 - Current buy price: 1.12345
2024-12-16 14:30:23 - tests.test_market_orders - [INFO] - test_market_orders.py:43 - Order data: {'volume': 0.1, 'stop_loss': 1.06728, 'take_profit': 1.17962}
```

**When to use**: Archive logs for historical analysis

### 2. Latest Test Run (latest_test_run.log)

**Purpose**: Quick access to most recent test execution

**Contains**: Same as timestamped log, but always overwritten

**Example**:
```
2024-12-16 14:30:22 - tests.test_market_orders - [INFO] - test_market_orders.py:35 - Starting test: Create market order with SL and TP
```

**When to use**: Quick debugging of the last test run

### 3. Pytest Log (pytest.log)

**Purpose**: Pytest framework output

**Contains**:
- Test discovery
- Test results (PASSED/FAILED)
- Print statements
- Warnings
- Errors

**Example**:
```
2024-12-16 14:30:20 [INFO] conftest.py:145 - ================================================================================
2024-12-16 14:30:20 [INFO] conftest.py:146 - STARTING TEST: test_create_market_order_with_stop_loss_and_take_profit
2024-12-16 14:30:20 [INFO] conftest.py:147 - ================================================================================
```

**When to use**: See pytest's perspective of test execution

## How to Use Logging in Tests

### Import the Logger

```python
from utils.logger import get_logger

logger = get_logger(__name__)
```

### Logging Levels

```python
# DEBUG - Detailed information for diagnosing problems
logger.debug(f"Variable value: {variable}")

# INFO - Confirmation that things are working as expected
logger.info("Test step completed successfully")

# WARNING - Something unexpected happened, but test continues
logger.warning("Using default value instead of configured value")

# ERROR - A serious problem occurred
logger.error(f"Failed to find element: {element_id}")
```

### Example Test with Logging

```python
import pytest
from utils.logger import get_logger

logger = get_logger(__name__)

def test_example(trading_page):
    """Example test with comprehensive logging"""

    logger.info("="*60)
    logger.info("Starting test_example")
    logger.info("="*60)

    # Log test data
    volume = 0.1
    logger.debug(f"Using volume: {volume}")

    # Log actions
    logger.info("Getting current buy price...")
    price = trading_page.get_current_buy_price()
    logger.info(f"Current buy price: {price}")

    # Log calculations
    stop_loss = price * 0.95
    logger.debug(f"Calculated stop loss: {stop_loss}")

    # Log test steps
    logger.info("Placing market order...")
    trading_page.place_market_order(volume=volume, stop_loss=stop_loss)
    logger.info("Market order placed successfully!")

    logger.info("Test completed successfully")
```

## Console Output

Logging also appears in the console while tests run:

**Console shows**: INFO level and above
**Files show**: DEBUG level and above

```bash
$ pytest tests/test_market_orders.py -v

14:30:22 - [INFO] - Starting test: Create market order with SL and TP
14:30:23 - [INFO] - Current buy price: 1.12345
14:30:25 - [INFO] - Market order placed successfully
```

## Debugging Failed Tests

### Step 1: Check Console Output

First, look at what pytest printed to console during the test run.

### Step 2: Check latest_test_run.log

```bash
# Windows
type logs\latest_test_run.log

# Linux/macOS
cat logs/latest_test_run.log
```

Look for:
- ERROR messages
- The last INFO message before failure
- Variable values logged before the error

### Step 3: Check Pytest Log

```bash
# Windows
type logs\pytest.log

# Linux/macOS
cat logs/pytest.log
```

Look for:
- Test result (PASSED/FAILED)
- Assertion errors
- Traceback information

### Step 4: Check Timestamped Log

For historical comparison:
```bash
ls logs/test_run_*.log  # See all run logs
cat logs/test_run_20241216_143022.log  # Check specific run
```

## Log Levels Explained

| Level | Console | File | Use Case |
|-------|---------|------|----------|
| DEBUG | ❌ | ✅ | Variable values, detailed flow |
| INFO | ✅ | ✅ | Test steps, confirmations |
| WARNING | ✅ | ✅ | Unexpected but handled situations |
| ERROR | ✅ | ✅ | Failures, exceptions |

## Best Practices

### 1. Log Test Boundaries

```python
def test_example():
    logger.info("="*60)
    logger.info("TEST START: test_example")
    logger.info("="*60)

    # ... test code ...

    logger.info("TEST END: test_example")
```

### 2. Log Test Data

```python
order_data = OrderDataGenerator.generate_market_order_data(price)
logger.debug(f"Generated order data: {order_data}")
```

### 3. Log Actions

```python
logger.info("Clicking order button...")
trading_page.click_order_button()
logger.info("Order button clicked")
```

### 4. Log Important Values

```python
current_price = trading_page.get_current_buy_price()
logger.info(f"Current price: {current_price}")
```

### 5. Log Assertions

```python
logger.info(f"Verifying {len(positions)} positions exist")
assert len(positions) > 0, "No positions found"
logger.info("Verification passed")
```

## Configuration

### Changing Log Levels

Edit `pytest.ini`:

```ini
# Console output level
log_cli_level = INFO  # Change to DEBUG for more console output

# File output level
log_file_level = DEBUG  # Already at DEBUG
```

### Changing Log Format

Edit `utils/logger.py`:

```python
# Detailed format (file logs)
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Simple format (console)
simple_formatter = logging.Formatter(
    '%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
```

## Troubleshooting Empty Logs

### Problem: Log files are empty

**Solutions**:

1. **Check if logger is imported**:
   ```python
   from utils.logger import get_logger
   logger = get_logger(__name__)
   ```

2. **Check if logger is used**:
   ```python
   logger.info("Test message")  # Make sure this is called
   ```

3. **Check log directory exists**:
   ```bash
   ls logs/  # Should see log files
   ```

4. **Run with verbose output**:
   ```bash
   pytest -v -s  # -s shows print statements
   ```

5. **Check file permissions**:
   Make sure `logs/` directory is writable

### Problem: Too much logging

**Solutions**:

1. **Reduce console logging**:
   Edit `pytest.ini`: `log_cli_level = WARNING`

2. **Reduce file logging**:
   Edit `pytest.ini`: `log_file_level = INFO`

3. **Disable console logging**:
   Edit `pytest.ini`: `log_cli = false`

## Example: Debugging a Failed Test

### Failed Test Output

```
FAILED tests/test_market_orders.py::test_create_market_order
```

### Check latest_test_run.log

```
2024-12-16 14:30:22 - tests.test_market_orders - [INFO] - Starting test
2024-12-16 14:30:23 - tests.test_market_orders - [INFO] - Current buy price: 1.12345
2024-12-16 14:30:23 - tests.test_market_orders - [DEBUG] - Order data: {...}
2024-12-16 14:30:25 - tests.test_market_orders - [INFO] - Clicking order button
2024-12-16 14:30:26 - pages.trading_page - [ERROR] - Order button not found
```

**Analysis**: The error occurred when clicking the order button. Check if the button locator is correct.

## Additional Debugging Tools

Besides logs, the framework provides:

1. **Screenshots on failure**: `screenshots/` directory
2. **Playwright traces**: `traces/` directory
3. **HTML reports**: `reports/` directory

## Quick Reference

| Task | Command |
|------|---------|
| View latest log | `cat logs/latest_test_run.log` |
| View pytest log | `cat logs/pytest.log` |
| List all logs | `ls logs/` |
| Run with debug console | `pytest -v -s --log-cli-level=DEBUG` |
| Clear old logs | `rm logs/test_run_*.log` |

## Summary

✅ **Two log files per run**: Timestamped + latest_test_run.log
✅ **Two logging systems**: Custom logger + pytest logging
✅ **Multi-level logging**: DEBUG (file) + INFO (console)
✅ **Structured format**: Timestamp, file, line number, message
✅ **Easy debugging**: Check latest_test_run.log first

For any logging issues, check:
1. Import statement
2. Logger usage in test
3. Log file permissions
4. pytest.ini configuration

Happy debugging! 🐛🔍
