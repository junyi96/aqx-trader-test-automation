"""
Stop Order Test Cases
Tests for creating stop orders with various expiry types
"""
import pytest
from playwright.sync_api import Page
from pages.trading_page import TradingPage
from pages.assets_page import AssetsPage
from utils.logger import get_logger
from utils.data_helpers import OrderDataGenerator

logger = get_logger(__name__)


@pytest.mark.stop_order
@pytest.mark.regression
class TestStopOrders:
    """Test cases for stop orders with different expiry types"""

    @pytest.mark.parametrize("expiry_type", [
        "Good Till Canceled",
        "Good Till Day",
        "Specified Date",
        "Specified Date and Time"
    ])
    def test_create_stop_order_with_expiry(
        self,
        trading_page: TradingPage,
        assets_page: AssetsPage,
        expiry_type: str
    ):
        """
        Data-driven test for creating stop orders with different expiry types

        Args:
            expiry_type: Type of order expiry to test
        """
        logger.info(f"Starting test: Create stop order with {expiry_type}")

        # Get current price
        current_price = trading_page.get_current_buy_price()
        logger.info(f"Current price: {current_price}")

        # Generate order data
        order_data = OrderDataGenerator.generate_stop_order_data(
            current_price,
            expiry_type=expiry_type
        )
        logger.info(f"Order data: {order_data}")

        # Place stop order
        trading_page.place_stop_order(**order_data)

        logger.info(f"Stop order created successfully with {expiry_type}")

        # Verify in pending orders
        assets_page.navigate_to_assets()
        assets_page.switch_to_pending_orders()

        pending_orders = assets_page.get_all_pending_orders()
        assert len(pending_orders) > 0, "No pending orders found after creating stop order"

        logger.info(f"Found {len(pending_orders)} pending order(s)")

    def test_stop_order_good_till_canceled(
        self,
        trading_page: TradingPage
    ):
        """Test creating a stop order with Good Till Canceled expiry"""
        logger.info("Testing Stop Order - Good Till Canceled")

        current_price = trading_page.get_current_buy_price()
        order_data = OrderDataGenerator.generate_stop_order_data(
            current_price,
            expiry_type="Good Till Canceled"
        )

        trading_page.place_stop_order(**order_data)
        logger.info("Stop order (GTC) created successfully")

    def test_stop_order_good_till_day(
        self,
        trading_page: TradingPage
    ):
        """Test creating a stop order with Good Till Day expiry"""
        logger.info("Testing Stop Order - Good Till Day")

        current_price = trading_page.get_current_buy_price()
        order_data = OrderDataGenerator.generate_stop_order_data(
            current_price,
            expiry_type="Good Till Day"
        )

        trading_page.place_stop_order(**order_data)
        logger.info("Stop order (GTD) created successfully")

    def test_stop_order_good_till_date(
        self,
        trading_page: TradingPage
    ):
        """Test creating a stop order with Specified Date expiry"""
        logger.info("Testing Stop Order - Specified Date")

        current_price = trading_page.get_current_buy_price()
        future_date = OrderDataGenerator.generate_future_date(days_ahead=7)

        order_data = OrderDataGenerator.generate_stop_order_data(
            current_price,
            expiry_type="Specified Date"
        )
        order_data["expiry_date"] = future_date

        trading_page.place_stop_order(**order_data)
        logger.info(f"Stop order (GTDate) created with expiry: {future_date}")

    def test_stop_order_good_till_date_and_time(
        self,
        trading_page: TradingPage
    ):
        """Test creating a stop order with Specified Date and Time expiry"""
        logger.info("Testing Stop Order - Specified Date and Time")

        current_price = trading_page.get_current_buy_price()
        future_datetime = OrderDataGenerator.generate_future_date(days_ahead=7)

        order_data = OrderDataGenerator.generate_stop_order_data(
            current_price,
            expiry_type="Specified Date and Time"
        )
        order_data["expiry_date"] = future_datetime

        trading_page.place_stop_order(**order_data)
        logger.info(f"Stop order (GTDateTime) created with expiry: {future_datetime}")