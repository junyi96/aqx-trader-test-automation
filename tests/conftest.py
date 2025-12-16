"""
Pytest configuration and fixtures for the test automation framework
Contains shared fixtures and hooks
"""
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, Playwright
from pathlib import Path
from datetime import datetime
from config.config import get_config
from pages.login_page import LoginPage
from pages.trading_page import TradingPage
from pages.assets_page import AssetsPage
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# Session-scoped fixtures
# ============================================================================

@pytest.fixture(scope="session")
def config():
    """Get test configuration"""
    cfg = get_config()
    cfg.create_directories()
    return cfg


@pytest.fixture(scope="session")
def browser_context(playwright: Playwright, config) -> BrowserContext:
    """
    Session-scoped browser context that persists across tests
    Maintains authentication state
    """
    logger.info(f"Launching browser: {config.BROWSER}")

    # Launch browser
    if config.BROWSER == "chromium":
        browser = playwright.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
    elif config.BROWSER == "firefox":
        browser = playwright.firefox.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
    elif config.BROWSER == "webkit":
        browser = playwright.webkit.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
    else:
        browser = playwright.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )

    # Create context
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="Asia/Singapore"
    )

    # Start tracing if enabled
    if config.SAVE_TRACE_ON_FAILURE:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # Stop tracing and save
    if config.SAVE_TRACE_ON_FAILURE:
        trace_path = config.TRACES_DIR / "trace.zip"
        context.tracing.stop(path=str(trace_path))
        logger.info(f"Trace saved to: {trace_path}")

    context.close()
    browser.close()


@pytest.fixture(scope="session")
def authenticated_page(browser_context: BrowserContext, config) -> Page:
    """
    Session-scoped page with login performed once
    All tests share this authenticated session
    """
    logger.info("Creating authenticated page session")

    page = browser_context.new_page()

    # Perform login
    login_page = LoginPage(page)
    logger.info(f"Logging in to: {config.BASE_URL}")
    login_page.login()
    logger.info("Login successful")

    yield page

    page.close()


# ============================================================================
# Function-scoped fixtures (per-test)
# ============================================================================

@pytest.fixture(scope="function")
def trading_page(authenticated_page: Page) -> TradingPage:
    """Get TradingPage instance"""
    return TradingPage(authenticated_page)


@pytest.fixture(scope="function")
def assets_page(authenticated_page: Page) -> AssetsPage:
    """Get AssetsPage instance"""
    return AssetsPage(authenticated_page)


# ============================================================================
# Pytest hooks
# ============================================================================

@pytest.fixture(autouse=True)
def log_test_execution(request, config):
    """Automatically log test start and end"""
    test_name = request.node.name
    logger.info("=" * 80)
    logger.info(f"STARTING TEST: {test_name}")
    logger.info("=" * 80)

    yield

    logger.info("=" * 80)
    logger.info(f"FINISHED TEST: {test_name}")
    logger.info("=" * 80)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and take screenshots on failure
    """
    outcome = yield
    report = outcome.get_result()

    # Only process on test call phase (not setup/teardown)
    if report.when == "call":
        config = get_config()

        # Get page fixture if available
        page = None
        if "authenticated_page" in item.fixturenames:
            page = item.funcargs.get("authenticated_page")

        if report.failed and page and config.TAKE_SCREENSHOT_ON_FAILURE:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{item.name}_{timestamp}_FAILED"
            screenshot_path = config.SCREENSHOTS_DIR / f"{screenshot_name}.png"

            try:
                page.screenshot(path=str(screenshot_path))
                logger.error(f"Test failed. Screenshot saved to: {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")


def pytest_configure(config):
    """Configure pytest"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "market_order: Tests for market orders"
    )
    config.addinivalue_line(
        "markers", "limit_order: Tests for limit orders"
    )
    config.addinivalue_line(
        "markers", "stop_order: Tests for stop orders"
    )
    config.addinivalue_line(
        "markers", "open_position: Tests for open position management"
    )
    config.addinivalue_line(
        "markers", "pending_order: Tests for pending orders"
    )
    config.addinivalue_line(
        "markers", "order_history: Tests for order history"
    )
    config.addinivalue_line(
        "markers", "smoke: Smoke tests"
    )
    config.addinivalue_line(
        "markers", "regression: Regression tests"
    )