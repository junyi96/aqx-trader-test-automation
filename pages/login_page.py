"""
Login Page Object
Handles all login-related interactions
"""
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object for login functionality"""

    # Locators
    USERNAME_INPUT = "login-user-id"
    PASSWORD_INPUT = "login-password"
    LOGIN_BUTTON = "login-submit"
    ANNOUNCEMENT_LOCATOR = '[id="0"]'
    USER_NAME_DISPLAY = "text=Lay Jun Yi"

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate(self):
        """Navigate to login page"""
        self.navigate_to(self.config.BASE_URL)

    def enter_username(self, username: str):
        """Enter username"""
        self.get_by_test_id(self.USERNAME_INPUT).fill(username)

    def enter_password(self, password: str):
        """Enter password"""
        self.get_by_test_id(self.PASSWORD_INPUT).fill(password)

    def click_login(self):
        """Click login button"""
        login_btn = self.get_by_test_id(self.LOGIN_BUTTON)
        expect(login_btn).to_be_enabled()
        login_btn.click()

    def verify_login_success(self, expected_username: str = "Lay Jun Yi", timeout: int = 15000):
        """Verify successful login"""
        # Wait for announcement
        announcement = self.page.locator(self.ANNOUNCEMENT_LOCATOR)
        expect(announcement).to_contain_text("Welcome to AQX Trader!", timeout=timeout)

        # Verify user name is visible
        user_name = self.page.locator(self.USER_NAME_DISPLAY)
        expect(user_name).to_be_visible(timeout=10000)

    def login(self, username: str = None, password: str = None):
        """
        Complete login flow
        Uses config credentials if not provided
        """
        username = username or self.config.USERNAME
        password = password or self.config.PASSWORD

        self.navigate()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        self.verify_login_success()