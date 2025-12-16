"""
Market Order Test Cases
Tests for creating and managing market orders
"""
import pytest
from playwright.sync_api import Page
from pages.trading_page import TradingPage
from pages.assets_page import AssetsPage
from utils.logger import get_logger
from utils.data_helpers import OrderDataGenerator

logger = get_logger(__name__)


@pytest.mark.market_order
@pytest.mark.smoke
class TestMarketOrders:
    """Test cases for market orders"""

    def test_create_market_order_with_stop_loss_and_take_profit(
        self,
        trading_page: TradingPage,
        assets_page: AssetsPage
    ):
        """
        Test creating a market order with stop loss and take profit

        Steps:
        1. Get current market price
        2. Calculate stop loss and take profit prices
        3. Place market order
        4. Verify order confirmation
        5. Verify order appears in open positions
        """
        logger.info("Starting test: Create market order with SL and TP")

        # Get current price
        current_price = trading_page.get_current_buy_price()
        logger.info(f"Current buy price: {current_price}")

        # Generate order data
        order_data = OrderDataGenerator.generate_market_order_data(current_price)
        logger.info(f"Order data: {order_data}")

        # Place market order
        trading_page.place_market_order(
            volume=order_data["volume"],
            stop_loss=order_data["stop_loss"],
            take_profit=order_data["take_profit"]
        )

        logger.info("Market order placed successfully")

        # Verify order in open positions
        assets_page.navigate_to_assets()
        assets_page.switch_to_open_positions()

        open_positions = assets_page.get_all_open_positions()
        assert len(open_positions) > 0, "No open positions found after placing market order"

        logger.info(f"Found {len(open_positions)} open position(s)")

    def test_market_order_auto_calculation(self, trading_page: TradingPage):
        """
        Test that stop loss and take profit points are auto-calculated

        Steps:
        1. Set volume
        2. Verify stop loss points field is populated
        3. Verify take profit points field is populated
        """
        logger.info("Testing auto-calculation of SL/TP points")
        #Make sure we are on trading page
        trading_page.navigate_to_trading()
        # Set volume to trigger auto-calculation
        trading_page.set_volume(0.1)

        #retrieve current price
        current_price = trading_page.get_current_buy_price()

        #prepare stoploss and takeprofit price data
        stop_loss_price = OrderDataGenerator.calculate_stop_loss(current_price)
        take_profit_price = OrderDataGenerator.calculate_take_profit(current_price)
        
        trading_page.set_stop_loss_price(stop_loss_price)
        trading_page.set_take_profit_price(take_profit_price)

        # Verify auto-calculated fields are populated
        trading_page.wait_for_auto_calculated_fields()

        logger.info("Auto-calculation verified successfully")