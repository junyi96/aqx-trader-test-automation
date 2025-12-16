"""
Examples of using the OrderType constants and confirmation mapping

This file demonstrates how to use the new order type management system.
"""
from constants.order_types import OrderType, OrderSide, OrderConfirmation


def example_confirmation_text():
    """Examples of getting confirmation text"""

    # Example 1: Market BUY order
    confirmation = OrderConfirmation.get_confirmation_text_by_name("Market", "BUY")
    print(f"Market BUY confirmation: {confirmation}")  # Output: "BUY"

    # Example 2: Market SELL order
    confirmation = OrderConfirmation.get_confirmation_text_by_name("Market", "SELL")
    print(f"Market SELL confirmation: {confirmation}")  # Output: "SELL"

    # Example 3: Limit BUY order
    confirmation = OrderConfirmation.get_confirmation_text_by_name("Limit", "BUY")
    print(f"Limit BUY confirmation: {confirmation}")  # Output: "BUY LIMIT"

    # Example 4: Limit SELL order
    confirmation = OrderConfirmation.get_confirmation_text_by_name("Limit", "SELL")
    print(f"Limit SELL confirmation: {confirmation}")  # Output: "SELL LIMIT"

    # Example 5: Stop BUY order
    confirmation = OrderConfirmation.get_confirmation_text_by_name("Stop", "BUY")
    print(f"Stop BUY confirmation: {confirmation}")  # Output: "BUY STOP"

    # Example 6: Stop SELL order
    confirmation = OrderConfirmation.get_confirmation_text_by_name("Stop", "SELL")
    print(f"Stop SELL confirmation: {confirmation}")  # Output: "SELL STOP"


def example_using_enums():
    """Examples using enum types directly"""

    # Using enum values
    confirmation = OrderConfirmation.get_confirmation_text(
        OrderType.MARKET,
        OrderSide.BUY
    )
    print(f"Using enums - Market BUY: {confirmation}")  # Output: "BUY"

    confirmation = OrderConfirmation.get_confirmation_text(
        OrderType.LIMIT,
        OrderSide.SELL
    )
    print(f"Using enums - Limit SELL: {confirmation}")  # Output: "SELL LIMIT"


def example_in_tests():
    """
    Example of how to use in actual tests

    In your test files, you would use it like:
    """
    # Example test code (pseudo-code)
    """
    def test_place_market_buy_order(trading_page):
        # Place a market BUY order
        trading_page.place_market_order(
            volume=0.1,
            order_side="BUY"  # The method will automatically verify "BUY" in confirmation
        )

    def test_place_limit_sell_order(trading_page):
        # Place a limit SELL order
        trading_page.place_limit_order(
            price=1.23456,
            volume=0.1,
            order_side="SELL"  # The method will automatically verify "SELL LIMIT" in confirmation
        )

    def test_place_stop_buy_order(trading_page):
        # Place a stop BUY order
        trading_page.place_stop_order(
            price=1.23456,
            volume=0.1,
            order_side="BUY"  # The method will automatically verify "BUY STOP" in confirmation
        )
    """
    pass


if __name__ == "__main__":
    print("=" * 60)
    print("Order Type Confirmation Examples")
    print("=" * 60)
    print()

    print("String-based examples:")
    print("-" * 60)
    example_confirmation_text()
    print()

    print("Enum-based examples:")
    print("-" * 60)
    example_using_enums()
