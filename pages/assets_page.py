"""
Assets Page Object
Handles interactions with open positions, pending orders, and order history
"""
from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
from typing import List, Optional
from datetime import datetime, timedelta


class AssetsPage(BasePage):
    """Page object for assets management (positions, orders, history)"""

    # Sidebar navigation
    ASSETS_TAB = "side-bar-option-assets"

    # Asset tabs
    OPEN_POSITIONS_TAB = "tab-asset-order-type-open-positions"
    PENDING_ORDERS_TAB = "tab-asset-order-type-pending-orders"
    HISTORY_TAB = "tab-asset-order-type-history"
    HISTORY_ORDERS_DEALS_TAB = "tab-asset-order-type-history-orders-and-deals"

    # List items
    OPEN_LIST_ITEM = "asset-open-list-item"
    PENDING_LIST_ITEM = "asset-pending-list-item"
    HISTORY_LIST_ITEM = "asset-history-position-list-item"

    # Position columns
    ORDER_ID_COLUMN = "asset-open-column-order-id"
    ORDER_DATETIME_COLUMN = "asset-open-column-open-date"
    HISTORY_ORDER_ID_COLUMN = "asset-history-column-order-id"
    HISTORY_OPEN_DATE_COLUMN = "asset-history-column-open-date"

    # Action buttons
    EDIT_BUTTON = "asset-open-button-edit"
    CLOSE_BUTTON = "asset-open-button-close"
    PENDING_EDIT_BUTTON = "asset-open-button-edit"

    # Close position dialog
    CLOSE_CONFIRMATION_TEXT = "Confirm To Close Position"
    VOLUME_INPUT = 'input[placeholder="Min: 0.01"]'
    MAX_BUTTON = "button:has-text('MAX')"

    # Overlay dialog
    OVERLAY_DIALOG = 'div[id="overlay-aqx-trader"]'

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_assets(self):
        """Navigate to assets tab"""
        self.get_by_test_id(self.ASSETS_TAB).click()

    def switch_to_open_positions(self):
        """Switch to open positions tab"""
        expect(self.get_by_test_id(self.OPEN_POSITIONS_TAB)).to_be_visible()
        self.get_by_test_id(self.OPEN_POSITIONS_TAB).click()

    def switch_to_pending_orders(self):
        """Switch to pending orders tab"""
        expect(self.get_by_test_id(self.PENDING_ORDERS_TAB)).to_be_visible()
        self.get_by_test_id(self.PENDING_ORDERS_TAB).click()

    def switch_to_history(self):
        """Switch to history tab"""
        self.get_by_test_id(self.HISTORY_TAB).click()
        self.get_by_test_id(self.HISTORY_ORDERS_DEALS_TAB).click()

    def get_all_open_positions(self) -> List[Locator]:
        """Get all open position rows"""
        self.wait_for_timeout(2000)  # Wait for data to load
        return self.get_by_test_id(self.OPEN_LIST_ITEM).all()

    def get_all_pending_orders(self) -> List[Locator]:
        """Get all pending order rows"""
        self.wait_for_timeout(2000)  # Wait for data to load
        return self.get_by_test_id(self.PENDING_LIST_ITEM).all()

    def get_all_history_items(self) -> List[Locator]:
        """Get all history items"""
        self.wait_for_timeout(2000)  # Wait for data to load
        return self.get_by_test_id(self.HISTORY_LIST_ITEM).all()

    def get_latest_open_position(self) -> Locator:
        """Get the latest (last) open position"""
        return self.get_by_test_id(self.OPEN_LIST_ITEM).last

    def get_latest_pending_order(self) -> Locator:
        """Get the latest (last) pending order"""
        return self.get_by_test_id(self.PENDING_LIST_ITEM).last

    def find_position_by_order_id(self, order_id: str) -> Optional[Locator]:
        """
        Find an open position by order ID

        Args:
            order_id: The order ID to search for

        Returns:
            Locator for the matching position, or None if not found
        """
        positions = self.get_all_open_positions()
        for position in positions:
            pos_id = position.get_by_test_id(self.ORDER_ID_COLUMN).text_content()
            if order_id in pos_id:
                return position
        return None
    
    def find_position_by_order_date(self, order_date: datetime) -> Optional[Locator]:
        """
        Find an open position by order ID

        Args:
            order_id: The order ID to search for

        Returns:
            Locator for the matching position, or None if not found
        """
        # e.g. 2025-12-17 08:47:10
        date_check = order_date.strftime("%Y-%m-%d %H:%M:%S")
        positions = self.get_all_open_positions()
        for position in positions:
            pos_date = position.get_by_test_id(self.ORDER_DATETIME_COLUMN).text_content()
            if date_check in pos_date:
                return position
        return None

    def verify_position_exists(self, order_id: str) -> bool:
        """Verify that a position with given order ID exists"""
        return self.find_position_by_order_id(order_id) is not None

    def edit_open_position(self, position: Locator = None):
        """
        Click edit button on a position

        Args:
            position: Specific position to edit, or None for latest
        """
        if position is None:
            position = self.get_latest_open_position()

        position.get_by_test_id(self.EDIT_BUTTON).click()

        # Wait for edit dialog to appear
        expect(self.get_by_text("Edit Position")).to_be_visible(timeout=10000)

    def close_position(
        self,
        position: Locator = None,
        volume: float = None,
        use_max: bool = False,
        verify_success: bool = True,
        order_datetime: datetime = datetime.now()
    ):
        """
        Close a position (full or partial)

        Args:
            position: Specific position to close, or None for latest
            volume: Volume to close (for partial close)
            use_max: Whether to use MAX button (full close)
            verify_success: Whether to verify success message
        """
        if position is None:
            position = self.get_latest_open_position()

        # Click close button
        position.get_by_test_id(self.CLOSE_BUTTON).click()

        # Wait for confirmation dialog
        expect(self.get_by_text(self.CLOSE_CONFIRMATION_TEXT)).to_be_visible(timeout=10000)
        expect(self.get_by_role("button").get_by_text("Confirm")).to_be_visible(timeout=10000)

        # Get order number before closing
        overlay = self.page.locator(self.OVERLAY_DIALOG)
        order_number_element = overlay.locator('div:has(div:text("Order No.")) + div').first
        order_number = order_number_element.text_content()

        # Set volume or use MAX
        if use_max:
            self.page.locator(self.MAX_BUTTON).click()
        elif volume is not None:
            self.page.locator(self.VOLUME_INPUT).fill(str(volume))

        # Confirm
        self.get_by_role("button").get_by_text("Confirm").click()

        # Verify success
        if verify_success:
            expect(self.get_by_text("Position has been closed.")).to_be_visible()

        return order_number

    def partial_close_position(self, position: Locator = None, volume_fraction: float = 0.5):
        """
        Partially close a position

        Args:
            position: Specific position to close
            volume_fraction: Fraction of volume to close (default 0.5 for half)
        """
        if position is None:
            position = self.get_latest_open_position()

        # Click close button
        position.get_by_test_id(self.CLOSE_BUTTON).click()

        # Wait for dialog
        expect(self.get_by_text(self.CLOSE_CONFIRMATION_TEXT)).to_be_visible(timeout=10000)

        # Get order number
        overlay = self.page.locator(self.OVERLAY_DIALOG)
        order_number_element = overlay.locator('div:text("Order No.") + div')
        order_number = order_number_element.text_content()

        # Get current volume and calculate partial
        current_volume = float(self.page.locator(self.VOLUME_INPUT).input_value())
        partial_volume = round(current_volume * volume_fraction, 2)

        # Fill partial volume
        self.page.locator(self.VOLUME_INPUT).fill(str(partial_volume))

        # Confirm
        self.get_by_role("button").get_by_text("Confirm").click()

        # Verify success
        expect(self.get_by_text("Position has been closed.")).to_be_visible()

        # Wait for list to refresh
        self.wait_for_timeout(4000)

        return order_number, partial_volume

    def verify_partial_close(self, order_id: str, expected_remaining_volume: float):
        """
        Verify that a partial close left the expected remaining volume

        Args:
            order_id: Order ID to check
            expected_remaining_volume: Expected remaining volume
        """
        position = self.find_position_by_order_id(order_id)
        if position is None:
            raise AssertionError(f"Order {order_id} not found after partial close")

        # Click to open close dialog to check volume
        position.get_by_test_id(self.CLOSE_BUTTON).click()
        expect(self.get_by_text(self.CLOSE_CONFIRMATION_TEXT)).to_be_visible(timeout=10000)

        remaining_volume = float(self.page.locator(self.VOLUME_INPUT).input_value())

        # Close the dialog (press Escape or cancel)
        self.page.keyboard.press("Escape")

        if remaining_volume != expected_remaining_volume:
            raise AssertionError(
                f"Volume mismatch: expected {expected_remaining_volume}, got {remaining_volume}"
            )

    def edit_pending_order(self, order: Locator = None):
        """
        Edit a pending order

        Args:
            order: Specific order to edit, or None for latest
        """
        if order is None:
            order = self.get_latest_pending_order()

        order.get_by_test_id(self.PENDING_EDIT_BUTTON).click()

        # Wait for edit dialog
        expect(self.get_by_text("Edit Order")).to_be_visible(timeout=10000)
        overlay = self.page.locator(self.OVERLAY_DIALOG)
        expect(overlay.locator('button:has-text("Confirm")')).to_be_visible(timeout=10000)

        return overlay

    def find_history_item_closest_to_time(self, target_time: datetime) -> Locator:
        """
        Find history item with open date closest to target time

        Args:
            target_time: The target datetime to match

        Returns:
            Locator for the closest history item
        """
        history_items = self.get_all_history_items()
        smallest_diff = timedelta.max
        closest_item = None

        for item in history_items:
            date_str = item.get_by_test_id(self.HISTORY_OPEN_DATE_COLUMN).text_content()
            item_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            time_diff = abs(target_time - item_date)

            if time_diff < smallest_diff:
                smallest_diff = time_diff
                closest_item = item

        return closest_item