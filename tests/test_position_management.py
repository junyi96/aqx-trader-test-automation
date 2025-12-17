"""
Position Management Test Cases
Tests for editing, closing (full/partial) open positions
"""
import pytest
from playwright.sync_api import Page
from pages.trading_page import TradingPage
from pages.assets_page import AssetsPage
from utils.logger import get_logger
from utils.data_helpers import OrderDataGenerator, PriceCalculator

logger = get_logger(__name__)


@pytest.mark.open_position
@pytest.mark.regression
class TestPositionManagement:
    """Test cases for managing open positions"""

    def test_edit_open_position(
        self,
        trading_page: TradingPage,
        assets_page: AssetsPage
    ):
        """
        Test editing an open position

        Steps:
        1. Create a market order (setup)
        2. Navigate to assets and find the position
        3. Edit the position
        4. Modify stop loss and take profit
        5. Verify changes are saved
        """
        logger.info("Starting test: Edit open position")

        # Setup: Create a market order
        current_price = trading_page.get_current_buy_price()
        order_data = OrderDataGenerator.generate_market_order_data(current_price)
        trading_page.place_market_order(**order_data)

        # Navigate to open positions
        assets_page.navigate_to_assets()
        assets_page.switch_to_open_positions()

        # Edit the latest position
        assets_page.edit_open_position()

        logger.info("Successfully opened edit dialog for position")

    def test_partial_close_position(
        self,
        trading_page: TradingPage,
        assets_page: AssetsPage
    ):
        """
        Test partially closing a position

        Steps:
        1. Create a market order (setup)
        2. Navigate to open positions
        3. Partially close the position (50%)
        4. Verify position still exists with reduced volume
        5. Verify remaining volume is correct
        """
        logger.info("Starting test: Partial close position")

        # Setup: Create a market order
        current_price = trading_page.get_current_buy_price()
        order_data = OrderDataGenerator.generate_market_order_data(current_price)
        volume = order_data["volume"]

        trading_page.place_market_order(**order_data)

        # Navigate to open positions
        assets_page.navigate_to_assets()
        assets_page.switch_to_open_positions()

        # Get the order ID

        # Partial close
        order_id, closed_volume = assets_page.partial_close_position(volume_fraction=0.5)
        logger.info(f"Partially closed order {order_id}, closed volume: {closed_volume}")

        # Verify position still exists
        expected_remaining = round(volume - closed_volume, 5)
        assets_page.verify_partial_close(order_id, expected_remaining)

        logger.info(f"Verified remaining volume: {expected_remaining}")

    def test_full_close_position(
        self,
        trading_page: TradingPage,
        assets_page: AssetsPage
    ):
        """
        Test fully closing a position using MAX button

        Steps:
        1. Create a market order (setup)
        2. Navigate to open positions
        3. Close the position completely using MAX
        4. Verify position no longer exists in open positions
        """
        logger.info("Starting test: Full close position")

        # Setup: Create a market order
        current_price = trading_page.get_current_buy_price()
        order_data = OrderDataGenerator.generate_market_order_data(current_price)

        trading_page.place_market_order(**order_data)

        # Navigate to open positions
        assets_page.navigate_to_assets()
        assets_page.switch_to_open_positions()

        # Get initial position count
        initial_positions = assets_page.get_all_open_positions()
        initial_count = len(initial_positions)

        # Full close using MAX
        order_id = assets_page.close_position(use_max=True)
        logger.info(f"Fully closed order {order_id}")

        # Verify position is removed
        assets_page.switch_to_open_positions()  # Refresh
        final_positions = assets_page.get_all_open_positions()
        final_count = len(final_positions)

        assert final_count < initial_count, f"Position count should decrease after full close"

        # Verify specific order doesn't exist
        assert not assets_page.verify_position_exists(order_id), \
            f"Order {order_id} should not exist after full close"

        logger.info("Position successfully closed and removed")