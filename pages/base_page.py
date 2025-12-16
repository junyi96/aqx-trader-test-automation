"""
Base Page Object class that all page objects inherit from.
Contains common functionality used across all pages.
"""
from playwright.sync_api import Page, expect, Locator
from typing import Optional
from config.config import get_config


class BasePage:
    """Base class for all page objects"""

    def __init__(self, page: Page):
        self.page = page
        self.config = get_config()
        self.timeout = self.config.DEFAULT_TIMEOUT

    def navigate_to(self, url: str = None):
        """Navigate to a URL"""
        if url is None:
            url = self.config.BASE_URL
        self.page.goto(url)

    def get_element(self, selector: str) -> Locator:
        """Get element by selector"""
        return self.page.locator(selector)

    def get_by_test_id(self, test_id: str) -> Locator:
        """Get element by test ID"""
        return self.page.get_by_test_id(test_id)

    def get_by_text(self, text: str, exact: bool = False) -> Locator:
        """Get element by text content"""
        return self.page.get_by_text(text, exact=exact)

    def get_by_role(self, role: str, name: str = None) -> Locator:
        """Get element by ARIA role"""
        return self.page.get_by_role(role, name=name)

    def click(self, selector: str, timeout: int = None):
        """Click an element"""
        timeout = timeout or self.timeout
        self.page.locator(selector).click(timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = None):
        """Fill an input field"""
        timeout = timeout or self.timeout
        self.page.locator(selector).fill(value, timeout=timeout)

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = None):
        """Wait for element to be in specific state"""
        timeout = timeout or self.timeout
        self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def wait_for_timeout(self, timeout: int):
        """Wait for a specific time (use sparingly)"""
        self.page.wait_for_timeout(timeout)

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is visible"""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False

    def expect_visible(self, locator: Locator, timeout: int = None):
        """Assert element is visible"""
        timeout = timeout or self.timeout
        expect(locator).to_be_visible(timeout=timeout)

    def expect_text(self, locator: Locator, text: str, timeout: int = None):
        """Assert element has specific text"""
        timeout = timeout or self.timeout
        expect(locator).to_have_text(text, timeout=timeout)

    def expect_value(self, locator: Locator, value: str, timeout: int = None):
        """Assert input has specific value"""
        timeout = timeout or self.timeout
        expect(locator).to_have_value(value, timeout=timeout)

    def take_screenshot(self, name: str):
        """Take a screenshot"""
        screenshot_path = self.config.SCREENSHOTS_DIR / f"{name}.png"
        self.page.screenshot(path=str(screenshot_path))
        return screenshot_path

    def get_input_value(self, selector: str) -> str:
        """Get value from input field"""
        return self.page.locator(selector).input_value()

    def get_text_content(self, selector: str) -> str:
        """Get text content of element"""
        return self.page.locator(selector).text_content()