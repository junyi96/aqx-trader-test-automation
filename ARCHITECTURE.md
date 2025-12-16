# Framework Architecture Documentation

## Overview

This document describes the architectural decisions and design patterns used in the AQX Trader Test Automation Framework.

## Design Principles

### 1. Separation of Concerns

The framework separates different responsibilities into distinct layers:

- **Page Objects**: Handle UI interactions
- **Tests**: Contain test logic and assertions
- **Utilities**: Provide reusable helper functions
- **Configuration**: Manage environment settings

### 2. DRY (Don't Repeat Yourself)

- Common functionality is abstracted into base classes
- Reusable test data generators
- Shared fixtures in conftest.py

### 3. SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Easy to extend without modifying existing code
- **Liskov Substitution**: Page objects can substitute BasePage
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions (BasePage)

## Architecture Layers

```
┌─────────────────────────────────────┐
│         Test Layer                  │
│  (test_*.py files)                  │
│  - Business logic                   │
│  - Assertions                       │
│  - Test data                        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Page Object Layer              │
│  (pages/*.py)                       │
│  - UI interactions                  │
│  - Element locators                 │
│  - Page-specific methods            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Utility Layer                  │
│  (utils/*.py)                       │
│  - Data generators                  │
│  - Custom waits                     │
│  - Logging                          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Configuration Layer              │
│  (config/config.py)                 │
│  - Environment settings             │
│  - Paths                            │
│  - Constants                        │
└─────────────────────────────────────┘
```

## Design Patterns

### 1. Page Object Model (POM)

**Purpose**: Encapsulate page interactions and locators

**Implementation**:
```python
# Base class with common functionality
class BasePage:
    def __init__(self, page: Page):
        self.page = page

# Specific page implementations
class LoginPage(BasePage):
    USERNAME_INPUT = "login-user-id"

    def enter_username(self, username: str):
        self.get_by_test_id(self.USERNAME_INPUT).fill(username)
```

**Benefits**:
- Maintainability: Locators in one place
- Reusability: Methods can be used across tests
- Readability: Tests read like user actions

### 2. Factory Pattern

**Purpose**: Create test data objects

**Implementation**:
```python
class OrderDataGenerator:
    @staticmethod
    def generate_market_order_data(current_price: float):
        return {
            "volume": 0.1,
            "stop_loss": calculate_stop_loss(current_price),
            "take_profit": calculate_take_profit(current_price),
        }
```

**Benefits**:
- Consistent test data
- Easy to modify data generation logic
- Reduces duplication

### 3. Fixture Pattern

**Purpose**: Manage test setup and teardown

**Implementation**:
```python
@pytest.fixture(scope="session")
def authenticated_page(browser_context):
    page = browser_context.new_page()
    login_page = LoginPage(page)
    login_page.login()
    yield page
    page.close()
```

**Benefits**:
- Reusable setup logic
- Automatic cleanup
- Scope control (session, function, class)

### 4. Strategy Pattern

**Purpose**: Different implementations for different scenarios

**Implementation**:
```python
class Config:
    pass

class DevelopmentConfig(Config):
    BASE_URL = "https://dev.example.com"

class ProductionConfig(Config):
    BASE_URL = "https://example.com"

def get_config():
    env = os.getenv("TEST_ENV", "development")
    return config_map[env]()
```

**Benefits**:
- Easy environment switching
- Extensible for new environments
- Centralized configuration

## Component Responsibilities

### BasePage

**Responsibilities**:
- Provide common page interaction methods
- Handle waits and timeouts
- Manage screenshots
- Provide assertion helpers

**Should NOT**:
- Contain test logic
- Have assertions in regular methods
- Know about specific pages

### Page Objects (LoginPage, TradingPage, etc.)

**Responsibilities**:
- Define page-specific locators
- Implement page-specific actions
- Return data when needed
- Handle page navigation

**Should NOT**:
- Contain assertions (except verification methods)
- Know about other pages (minimize coupling)
- Have business logic

### Tests

**Responsibilities**:
- Define test scenarios
- Make assertions
- Orchestrate page objects
- Use test data generators

**Should NOT**:
- Interact with Playwright directly
- Duplicate code
- Have hard-coded test data

### Utilities

**Responsibilities**:
- Provide helper functions
- Generate test data
- Handle logging
- Provide custom waits

**Should NOT**:
- Have page-specific logic
- Contain test scenarios

### Configuration

**Responsibilities**:
- Manage environment settings
- Define paths
- Store constants
- Handle environment variables

**Should NOT**:
- Contain business logic
- Have page interactions

## Data Flow

```
Test Case
    │
    ├──> Gets fixture (authenticated_page)
    │       └──> Uses LoginPage
    │               └──> Uses BasePage methods
    │                       └──> Interacts with Playwright
    │
    ├──> Uses OrderDataGenerator
    │       └──> Returns test data
    │
    ├──> Uses TradingPage methods
    │       └──> Uses BasePage methods
    │               └──> Interacts with Playwright
    │
    └──> Makes assertions
```

## Error Handling Strategy

### 1. Retry Logic

For flaky operations:
```python
RetryHelper.retry_on_exception(
    func=lambda: element.click(),
    max_attempts=3,
    delay=1000
)
```

### 2. Custom Waits

For dynamic content:
```python
CustomWaits.wait_for_numeric_value(locator, timeout=10000)
```

### 3. Graceful Failures

- Screenshot on failure (automatic)
- Trace recording (automatic)
- Detailed logging (automatic)

## Extensibility

### Adding a New Page Object

1. Create new file in `pages/`
2. Inherit from `BasePage`
3. Define locators as class constants
4. Implement page-specific methods

### Adding a New Test Suite

1. Create new file in `tests/`
2. Use existing fixtures
3. Follow naming convention: `test_*.py`
4. Add appropriate markers

### Adding New Configuration

1. Add to `config/config.py`
2. Create new config class
3. Add to `config_map`
4. Document in README

## Performance Considerations

### 1. Session-Scoped Fixtures

Authenticate once per session:
```python
@pytest.fixture(scope="session")
def authenticated_page():
    # Login once, reuse across tests
```

### 2. Parallel Execution

Tests are designed to be independent:
```bash
pytest -n auto  # Run in parallel
```

### 3. Smart Waits

Use explicit waits instead of `sleep()`:
```python
expect(element).to_be_visible(timeout=10000)
```

## Security Considerations

### 1. Credential Management

- Never hard-code credentials
- Use environment variables
- Use `.env` file (git-ignored)
- Use secrets in CI/CD

### 2. Sensitive Data

- Screenshots may contain sensitive data
- Traces may contain sensitive data
- Don't commit test artifacts
- Clean up after test runs

## Testing Best Practices Implemented

1. ✅ Atomic tests (independent, isolated)
2. ✅ Deterministic tests (same input = same output)
3. ✅ Fast feedback (parallel execution)
4. ✅ Clear naming (descriptive test names)
5. ✅ Minimal setup (fixtures handle it)
6. ✅ No hard-coded waits (explicit waits only)
7. ✅ Proper cleanup (automatic via fixtures)
8. ✅ Comprehensive logging (multi-level)

## Maintenance Guidelines

### When to Refactor

- When a locator changes in multiple places → Move to page object
- When test data is duplicated → Create data generator
- When setup is repeated → Create fixture
- When logic is complex → Extract to utility

### Code Review Checklist

- [ ] Uses page objects (not raw Playwright calls)
- [ ] Has appropriate test markers
- [ ] Includes logging
- [ ] Uses data generators for test data
- [ ] No hard-coded waits
- [ ] Descriptive test name
- [ ] Has docstring
- [ ] Follows naming conventions

## Future Enhancements

Possible improvements:

1. **API Integration**: Use API for test data setup
2. **Visual Testing**: Add visual regression tests
3. **Performance Testing**: Add performance benchmarks
4. **Accessibility Testing**: Add a11y checks
5. **Database Integration**: Validate against database
6. **Mobile Testing**: Add mobile browser support
7. **Cross-browser Grid**: Selenium Grid or BrowserStack
8. **AI-Powered Testing**: Self-healing locators