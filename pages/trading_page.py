"""
Trading Page Object
Handles all trading-related interactions (market orders, limit orders, stop orders)
"""
from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
from datetime import datetime, timedelta
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

    def get_current_buy_price(self, timeout: int = 10000) -> float:
        """Get current buy price"""
        price_element = self.get_by_test_id(self.BUY_PRICE)

        # Wait for price to be populated with actual numbers
        expect(price_element).not_to_be_empty(timeout=timeout)

        price_text = price_element.text_content()
        # Extract numeric value from price
        price_match = re.search(r'[\d.]+', price_text)
        if price_match:
            return float(price_match.group())
        raise ValueError(f"Could not extract price from: {price_text}")

    def get_current_sell_price(self, timeout: int = 10000) -> float:
        """Get current sell price"""
        price_element = self.get_by_test_id(self.SELL_PRICE)
        expect(price_element).not_to_be_empty(timeout=timeout)

        price_text = price_element.text_content()
        price_match = re.search(r'[\d.]+', price_text)
        if price_match:
            return float(price_match.group())
        raise ValueError(f"Could not extract price from: {price_text}")

    def set_volume(self, volume: float):
        """Set trading volume"""
        self.get_by_test_id(self.VOLUME_INPUT).fill(str(volume))

    def wait_for_auto_calculated_fields(self, timeout: int = 10000):
        """Wait for stop loss and take profit points to be auto-calculated"""
        expect(self.get_by_test_id(self.STOP_LOSS_POINTS)).not_to_be_empty(timeout=timeout)
        expect(self.get_by_test_id(self.TAKE_PROFIT_POINTS)).not_to_be_empty(timeout=timeout)

    def set_stop_loss_price(self, price: float):
        """Set stop loss price"""
        self.get_by_test_id(self.STOP_LOSS_PRICE).fill(str(price))

    def set_take_profit_price(self, price: float):
        """Set take profit price"""
        self.get_by_test_id(self.TAKE_PROFIT_PRICE).fill(str(price))

    def get_stop_loss_price(self) -> float:
        """Get current stop loss price"""
        return float(self.get_by_test_id(self.STOP_LOSS_PRICE).input_value())

    def get_take_profit_price(self) -> float:
        """Get current take profit price"""
        return float(self.get_by_test_id(self.TAKE_PROFIT_PRICE).input_value())

    def select_order_type(self, order_type: str):
        """
        Select order type
        Args:
            order_type: "MARKET", "LIMIT", or "STOP"
        """
        self.get_by_test_id(self.ORDER_TYPE_DROPDOWN).click()
        self.get_by_text(order_type, exact=True).click()

    def select_expiry_type(self, expiry_type: str):
        """
        Select expiry type for pending orders
        Args:
            expiry_type: "Good Till Canceled", "Good Till Day",
                        "Good Till Specified Date", "Good Till Specified Date and Time"
        """
        self.get_by_test_id(self.EXPIRY_DROPDOWN).click()
        # Handle multiple elements with same text (use second one)
        elements = self.get_by_text(expiry_type, exact=True).all()
        if len(elements) > 1:
            elements[1].click()
        else:
            elements[0].click()

    def set_limit_price(self, price: float):
        """Set limit/stop order price"""
        self.page.locator(self.PRICE_INPUT).fill(str(price))

    def get_limit_price(self) -> float:
        """Get limit/stop order price"""
        return float(self.page.locator(self.PRICE_INPUT).input_value())

    def click_order_button(self):
        """Click the order button"""
        order_button = self.get_by_test_id(self.ORDER_BUTTON)
        expect(order_button).to_be_enabled()
        order_button.click()

    def verify_confirmation_dialog(self, order_type: str, timeout: int = 10000):
        """Verify confirmation dialog appears with correct order type"""
        expect(self.get_by_test_id(self.CONFIRM_BUTTON)).to_be_visible(timeout=timeout)
        expect(self.get_by_test_id(self.CONFIRMATION_ORDER_TYPE)).to_have_text(order_type, timeout=timeout)

    def confirm_order(self):
        """Click confirm button in confirmation dialog"""
        self.get_by_test_id(self.CONFIRM_BUTTON).click()

    def verify_order_success(self, message: str = None, timeout: int = 10000):
        """Verify order creation success"""
        if message is None:
            message = "Position has been created"
        expect(self.get_by_text(message)).to_be_visible(timeout=timeout)

    def place_market_order(
        self,
        volume: float = 0.1,
        stop_loss: float = None,
        take_profit: float = None,
        verify_success: bool = True
    ):
        """
        Complete flow to place a market order

        Args:
            volume: Trading volume
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            verify_success: Whether to verify success message
        """
        # Set volume
        self.set_volume(volume)

        # Wait for auto-calculated fields
        self.wait_for_auto_calculated_fields()

        # Set stop loss and take profit if provided
        if stop_loss:
            self.set_stop_loss_price(stop_loss)
        if take_profit:
            self.set_take_profit_price(take_profit)

        # Click order button
        self.click_order_button()

        # Verify and confirm
        self.verify_confirmation_dialog("BUY")
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
        verify_success: bool = True
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
            verify_success: Whether to verify success message
        """
        # Select LIMIT order type
        self.select_order_type("LIMIT")

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
        self.verify_confirmation_dialog("BUY LIMIT")
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
        verify_success: bool = True
    ):
        """
        Complete flow to place a stop order
        Similar to place_limit_order but for STOP orders
        """
        # Select STOP order type
        self.select_order_type("STOP")

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
        self.verify_confirmation_dialog("BUY STOP")
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
        # Click on date input to open calendar
        self.get_by_test_id("trade-input-expiry-date").click()

        # Click on the date (using aria-label)
        day_str = expiry_date.strftime("%Y-%m-%d")
        self.page.locator(f'div[aria-label="{day_str}"]').click()

        # If time is needed, set it
        if include_time:
            time_str = expiry_date.strftime("%H:%M")
            self.get_by_test_id("trade-input-expiry-time").fill(time_str)