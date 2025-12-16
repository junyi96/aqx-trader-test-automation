"""
Order type constants and mappings
Defines order types, order sides, and their expected confirmation text
"""
from enum import Enum


class OrderType(Enum):
    """Order type definitions"""
    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"
    STOP_LIMIT = "Stop Limit"


class OrderSide(Enum):
    """Order side (direction)"""
    BUY = "BUY"
    SELL = "SELL"


class OrderConfirmation:
    """Maps order types and sides to their confirmation dialog text"""

    @staticmethod
    def get_confirmation_text(order_type: OrderType, order_side: OrderSide) -> str:
        """
        Get expected confirmation text for an order type and side

        Args:
            order_type: OrderType enum value
            order_side: OrderSide enum value (BUY or SELL)

        Returns:
            Confirmation dialog text

        Examples:
            >>> OrderConfirmation.get_confirmation_text(OrderType.MARKET, OrderSide.BUY)
            'BUY'
            >>> OrderConfirmation.get_confirmation_text(OrderType.LIMIT, OrderSide.SELL)
            'SELL LIMIT'
        """
        # Market orders only show BUY or SELL
        if order_type == OrderType.MARKET:
            return order_side.value

        # Other order types show "SIDE TYPE" (e.g., "BUY LIMIT", "SELL STOP")
        return f"{order_side.value} {order_type.value.upper()}"

    @staticmethod
    def get_confirmation_text_by_name(order_type_name: str, order_side_name: str) -> str:
        """
        Get expected confirmation text by order type and side names

        Args:
            order_type_name: Order type string (e.g., "Market", "Limit")
            order_side_name: Order side string ("BUY" or "SELL")

        Returns:
            Confirmation dialog text

        Examples:
            >>> OrderConfirmation.get_confirmation_text_by_name("Market", "BUY")
            'BUY'
            >>> OrderConfirmation.get_confirmation_text_by_name("Limit", "SELL")
            'SELL LIMIT'
        """
        # Find matching OrderType
        order_type = None
        for ot in OrderType:
            if ot.value == order_type_name:
                order_type = ot
                break

        if order_type is None:
            raise ValueError(f"Unknown order type: {order_type_name}")

        # Find matching OrderSide
        order_side = None
        for os in OrderSide:
            if os.value == order_side_name.upper():
                order_side = os
                break

        if order_side is None:
            raise ValueError(f"Unknown order side: {order_side_name}")

        return OrderConfirmation.get_confirmation_text(order_type, order_side)
