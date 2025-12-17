"""
Trading Page Object
Handles all trading-related interactions (market orders, limit orders, stop orders)
"""
from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
from datetime import datetime, timedelta
from constants.order_types import OrderType, OrderSide, OrderConfirmation
import re


class TradingPage(BasePage):
    """Page object for trading functionality"""

    # Locators
    BUY_PRICE = "trade-live-buy-price"
    SELL_PRICE = "trade-live-sell-price"
    VOLUME_INPUT = "trade-input-volume"
    STOP_LOSS_PRICE = "trade-input-stoploss-price"
    TAKE_PROFIT_PRICE = "trade-input-takeprofit-price"
    STOP_LOSS_POINTS = "trade-input-stoploss-points"
    TAKE_PROFIT_POINTS = "trade-input-takeprofit-points"
    ORDER_TYPE_DROPDOWN = "trade-dropdown-order-type"
    EXPIRY_DROPDOWN = "trade-dropdown-expiry"
    PRICE_INPUT = 'input[name="price"]'
    ORDER_BUTTON = "trade-button-order"

    # Confirmation dialog
    CONFIRM_BUTTON = "trade-confirmation-button-confirm"
    CONFIRMATION_ORDER_TYPE = "trade-confirmation-order-type"
    CONFIRMATION_VALUES = 'div[data-testid="trade-confirmation-value"]'

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_trading(self):
        """Navigate to the trading page"""
        self.navigate_to(f"{self.config.BASE_URL}/web/trade")

    def verify_on_trading_page(self, timeout: int = 5000) -> bool:
        """Verify that we are on the trading page by checking for key elements
        Returns:
        bool: True if on trading page, False otherwise
        """
        try:
            # Check for the buy price element which is unique to trading page
            expect(self.get_by_test_id(self.BUY_PRICE)).to_be_visible(timeout=timeout)
            # Check for the order button
            expect(self.get_by_test_id(self.ORDER_BUTTON)).to_be_visible(timeout=timeout)
            return True
        except:
            return False
    
    def check_on_trading_page_and_navigate(self, timeout: int = 1000):
        """
        Check if we are on the trading page, and navigate there if not

        Uses a short timeout (1 second) to quickly detect wrong page
        """
        if not self.verify_on_trading_page(timeout=timeout):
            self.navigate_to_trading()
            # Verify we successfully navigated
            self.verify_on_trading_page(timeout=timeout)

    def get_current_buy_price(self, timeout: int = 5000) -> float:
        self.check_on_trading_page_and_navigate()

        """Get current buy price"""
        price_element = self.get_by_test_id(self.BUY_PRICE)

        # Wait for price to load (not show placeholder "--")
        expect(price_element).not_to_have_text("--", timeout=timeout)
        # Wait for price to be a number (with optional decimals)
        expect(price_element).to_have_text(re.compile(r'^\d+\.?\d*$'), timeout=timeout)

        price_text = price_element.text_content()
        # Extract numeric value from price
        price_match = re.search(r'[\d.]+', price_text)
        if price_match:
            return float(price_match.group())
        raise ValueError(f"Could not extract buy price from: {price_text}")

    def get_current_sell_price(self, timeout: int = 10000) -> float:
        self.check_on_trading_page_and_navigate()

        """Get current sell price"""
        price_element = self.get_by_test_id(self.SELL_PRICE)

        # Wait for price to load (not show placeholder "--")
        expect(price_element).not_to_have_text("--", timeout=timeout)

        price_text = price_element.text_content()
        price_match = re.search(r'[\d.]+', price_text)
        if price_match:
            return float(price_match.group())
        raise ValueError(f"Could not extract sell price from: {price_text}")

    def set_volume(self, volume: float):
        self.check_on_trading_page_and_navigate()
        """Set trading volume"""
        self.get_by_test_id(self.VOLUME_INPUT).fill(str(volume))

    def wait_for_auto_calculated_fields(self, timeout: int = 10000):
        """Wait for stop loss and take profit points to be auto-calculated"""
        self.check_on_trading_page_and_navigate()
        expect(self.get_by_test_id(self.STOP_LOSS_POINTS)).not_to_be_empty(timeout=timeout)
        expect(self.get_by_test_id(self.TAKE_PROFIT_POINTS)).not_to_be_empty(timeout=timeout)

    def set_stop_loss_price(self, price: float):
        """Set stop loss price"""
        self.check_on_trading_page_and_navigate()
        self.get_by_test_id(self.STOP_LOSS_PRICE).fill(str(price))
        self.get_by_test_id(self.STOP_LOSS_POINTS).click()  # Trigger any onchange events

    def set_take_profit_price(self, price: float):
        """Set take profit price"""
        self.check_on_trading_page_and_navigate()
        self.get_by_test_id(self.TAKE_PROFIT_PRICE).fill(str(price))
        self.get_by_test_id(self.TAKE_PROFIT_POINTS).click()  # Trigger any onchange events

    def get_stop_loss_price(self) -> float:
        """Get current stop loss price"""
        self.check_on_trading_page_and_navigate()
        return float(self.get_by_test_id(self.STOP_LOSS_PRICE).input_value())

    def get_take_profit_price(self) -> float:
        """Get current take profit price"""
        self.check_on_trading_page_and_navigate()
        return float(self.get_by_test_id(self.TAKE_PROFIT_PRICE).input_value())

    def select_order_type(self, order_type: str):
        """
        Select order type
        Args:
            order_type: "MARKET", "LIMIT", or "STOP"
        """
        self.check_on_trading_page_and_navigate()

        order_type_element = self.get_by_test_id(self.ORDER_TYPE_DROPDOWN)
        order_type_element.click()
        
        #get the last matching element as that is where the dropdown options are
        order_type_element.get_by_text(order_type, exact=True).last.click()

    def select_expiry_type(self, expiry_type: str):
        """
        Select expiry type for pending orders
        Args:
            expiry_type: "Good Till Canceled", "Good Till Day",
                        "Good Till Specified Date", "Good Till Specified Date and Time"
        """
        self.check_on_trading_page_and_navigate()

        expiry_type_element = self.get_by_test_id(self.EXPIRY_DROPDOWN)
        expiry_type_element.click()

        # Handle multiple elements with same text (use second one)
        #elements = expiry_type_element_dropdown.get_by_text(expiry_type, exact=True).all()
        #if len(elements) > 1:
        #    elements[1].click()
        #else:
        #    elements[0].click()
        #get the last matching element as that is where the dropdown options are
        expiry_type_element.get_by_text(expiry_type, exact=True).last.click()

    def set_limit_price(self, price: float):
        """Set limit/stop order price"""
        self.check_on_trading_page_and_navigate()

        self.page.locator(self.PRICE_INPUT).fill(str(price))

    def get_limit_price(self) -> float:
        """Get limit/stop order price"""
        self.check_on_trading_page_and_navigate()

        return float(self.page.locator(self.PRICE_INPUT).input_value())

    def click_order_button(self):
        """Click the order button"""
        self.check_on_trading_page_and_navigate()

        order_button = self.get_by_test_id(self.ORDER_BUTTON)
        expect(order_button).to_be_enabled()
        order_button.click()

    def verify_confirmation_dialog(self, order_type_name: str, order_side: str = "BUY", timeout: int = 10000):
        """
        Verify confirmation dialog appears with correct order type

        Args:
            order_type_name: Order type ("Market", "Limit", "Stop", etc.)
            order_side: Order side ("BUY" or "SELL")
            timeout: Timeout in milliseconds
        """
        self.check_on_trading_page_and_navigate()
        expect(self.get_by_test_id(self.CONFIRM_BUTTON)).to_be_visible(timeout=timeout)

        # Get expected confirmation text based on order type and side
        expected_text = OrderConfirmation.get_confirmation_text_by_name(order_type_name, order_side)
        expect(self.get_by_test_id(self.CONFIRMATION_ORDER_TYPE)).to_have_text(expected_text, timeout=timeout)

    def confirm_order(self):
        """Click confirm button in confirmation dialog"""
        self.check_on_trading_page_and_navigate()

        self.get_by_test_id(self.CONFIRM_BUTTON).click()

    def verify_order_success(self, message: str = None, timeout: int = 10000):
        """Verify order creation success"""
        self.check_on_trading_page_and_navigate()

        if message is None:
            message = "Position has been created"
        expect(self.get_by_text(message)).to_be_visible(timeout=timeout)

    def place_market_order(
        self,
        volume: float = 0.1,
        stop_loss: float = None,
        take_profit: float = None,
        order_side: str = "BUY",
        verify_success: bool = True,
        order_datetime: datetime = datetime.now()
    ):
        """
        Complete flow to place a market order

        Args:
            volume: Trading volume
            stop_loss: Stop loss points (optional)
            take_profit: Take profit points (optional)
            order_side: Order side - "BUY" or "SELL" (default: "BUY")
            verify_success: Whether to verify success message
        """
        self.check_on_trading_page_and_navigate()

        #Make sure it is market order
        self.select_order_type("Market")

        # Set volume
        self.set_volume(volume)

        # auto-calculated fields will be empty with no price for either stoploss or takeprofit
        #self.wait_for_auto_calculated_fields()

        # Set stop loss and take profit prices based on if provided
        if stop_loss:
            self.set_stop_loss_price(stop_loss)
        if take_profit:
            self.set_take_profit_price(take_profit)

        # Click order button
        self.click_order_button()

        # Verify and confirm
        self.verify_confirmation_dialog("Market", order_side)
        self.confirm_order()

        # Verify success
        if verify_success:
            self.verify_order_success()

    def place_limit_order(
        self,
        price: float,
        volume: float = 0.1,
        expiry_type: str = "Good Till Canceled",
        stop_loss: float = None,
        take_profit: float = None,
        expiry_date: datetime = None,
        order_side: str = "BUY",
        verify_success: bool = True,
        order_datetime: datetime = datetime.now()
    ):
        """
        Complete flow to place a limit order

        Args:
            price: Limit price
            volume: Trading volume
            expiry_type: Type of expiry
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            expiry_date: Expiry date for date-based expiry types
            order_side: Order side - "BUY" or "SELL" (default: "BUY")
            verify_success: Whether to verify success message
        """
        self.check_on_trading_page_and_navigate()

        # Select LIMIT order type
        self.select_order_type("Limit")

        # Set limit price
        self.set_limit_price(price)

        # Set volume
        self.set_volume(volume)

        # Set stop loss and take profit if provided
        if stop_loss:
            self.set_stop_loss_price(stop_loss)
        if take_profit:
            self.set_take_profit_price(take_profit)

        # Select expiry type
        self.select_expiry_type(expiry_type)

        # Handle date selection if needed
        if expiry_date and "Date" in expiry_type:
            self._set_expiry_date(expiry_date, include_time="Time" in expiry_type)

        # Click order button
        self.click_order_button()

        # Verify and confirm
        self.verify_confirmation_dialog("Limit", order_side)
        self.confirm_order()

        # Verify success
        if verify_success:
            self.verify_order_success("Order has been created.")

    def place_stop_order(
        self,
        price: float,
        volume: float = 0.1,
        expiry_type: str = "Good Till Canceled",
        stop_loss: float = None,
        take_profit: float = None,
        expiry_date: datetime = None,
        order_side: str = "BUY",
        verify_success: bool = True
    ):
        """
        Complete flow to place a stop order

        Args:
            price: Stop price
            volume: Trading volume
            expiry_type: Type of expiry
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            expiry_date: Expiry date for date-based expiry types
            order_side: Order side - "BUY" or "SELL" (default: "BUY")
            verify_success: Whether to verify success message
        """
        self.check_on_trading_page_and_navigate()

        # Select STOP order type
        self.select_order_type("Stop")

        # Set stop price
        self.set_limit_price(price)

        # Set volume
        self.set_volume(volume)

        # Set stop loss and take profit if provided
        if stop_loss:
            self.set_stop_loss_price(stop_loss)
        if take_profit:
            self.set_take_profit_price(take_profit)

        # Select expiry type
        self.select_expiry_type(expiry_type)

        # Handle date selection if needed
        if expiry_date and "Date" in expiry_type:
            self._set_expiry_date(expiry_date, include_time="Time" in expiry_type)

        # Click order button
        self.click_order_button()

        # Verify and confirm
        self.verify_confirmation_dialog("Stop", order_side)
        self.confirm_order()

        # Verify success
        if verify_success:
            self.verify_order_success("Order has been created.")

    def _set_expiry_date(self, expiry_date: datetime, include_time: bool = False):
        """
        Internal method to set expiry date in calendar picker

        Args:
            expiry_date: The date to set
            include_time: Whether to also set time
        """
        #self.check_on_trading_page_and_navigate()

        # Click on date input to open calendar
        self.get_by_test_id("trade-input-expiry-date").click()

        # Click on the date (using aria-label)
        # example: aria-label="December 24, 2025"
        day_str = expiry_date.strftime("%B %d, %Y")
        self.page.locator(f'abbr[aria-label="{day_str}"]').click()

        # If time is needed, set it
        if include_time:
            time_hr_str = expiry_date.strftime("%H")
            time_min_str = expiry_date.strftime("%M")

            # click on time dropdown to open
            self.get_by_test_id("trade-input-expiry-time").click()
            self.wait_for_timeout(3000)  # Wait for picker to render
            

            #click on hour to set
            self.page.locator('div:has-text("Hour") + div').first.click()
            # Wait for the dropdown options to appear
            self.page.wait_for_selector('div[data-testid="options"]', timeout=5000)
            self.page.locator(f'[data-testid="options"] div:has-text("{time_hr_str}")').first.click()
            
            #click on minute to set
            self.page.locator('div:has-text("Minute") + div').first.click()
            # Wait for the dropdown options to appear
            self.page.wait_for_selector('div[data-testid="options"]', timeout=5000)
            self.page.locator(f'[data-testid="options"] div:has-text("{time_min_str}")').first.click()
            # click OK to confirm time
            self.page.get_by_role("button", name="OK").click()