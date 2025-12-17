"""
Data helper utilities for test automation
Provides functions for test data generation and manipulation
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any


class OrderDataGenerator:
    """Generate test data for orders"""

    @staticmethod
    def generate_volume(min_vol: float = 0.01, max_vol: float = 1.0) -> float:
        """Generate random trading volume"""
        return round(random.uniform(min_vol, max_vol), 2)

    @staticmethod
    def calculate_stop_loss(current_price: float, percentage: float = 5.0) -> float:
        """
        Calculate stop loss price

        Args:
            current_price: Current market price
            percentage: Percentage below current price

        Returns:
            Stop loss price
        """
        return round(current_price * (1 - percentage / 100), 5)

    @staticmethod
    def calculate_take_profit(current_price: float, percentage: float = 5.0) -> float:
        """
        Calculate take profit price

        Args:
            current_price: Current market price
            percentage: Percentage above current price

        Returns:
            Take profit price
        """
        return round(current_price * (1 + percentage / 100), 5)

    @staticmethod
    def calculate_limit_price(current_price: float, below_market: bool = True) -> float:
        """
        Calculate limit order price

        Args:
            current_price: Current market price
            below_market: True for buy limit (below market), False for above market

        Returns:
            Limit price
        """
        if below_market:
            return round(current_price * 0.99, 5)  # 1% below market
        else:
            return round(current_price * 1.01, 5)  # 1% above market

    @staticmethod
    def calculate_stop_price(current_price: float, above_market: bool = True) -> float:
        """
        Calculate stop order price

        Args:
            current_price: Current market price
            above_market: True for buy stop (above market), False for below market

        Returns:
            Stop price
        """
        if above_market:
            return round(current_price * 1.01, 5)  # 1% above market
        else:
            return round(current_price * 0.99, 5)  # 1% below market

    @staticmethod
    def generate_future_date(days_ahead: int = 7) -> datetime:
        """
        Generate a future date

        Args:
            days_ahead: Number of days in the future

        Returns:
            Future datetime
        """
        return datetime.now() + timedelta(days=days_ahead)

    @staticmethod
    def generate_market_order_data(current_price: float) -> Dict[str, Any]:
        """
        Generate complete market order test data

        Args:
            current_price: Current market price

        Returns:
            Dictionary with order data
        """
        return {
            "volume": 0.1,
            "stop_loss": OrderDataGenerator.calculate_stop_loss(current_price),
            "take_profit": OrderDataGenerator.calculate_take_profit(current_price),
            "order_datetime": datetime.now()
        }

    @staticmethod
    def generate_limit_order_data(current_price: float, expiry_type: str = "Good Till Canceled") -> Dict[str, Any]:
        """
        Generate complete limit order test data

        Args:
            current_price: Current market price
            expiry_type: Type of expiry

        Returns:
            Dictionary with order data
        """
        limit_price = OrderDataGenerator.calculate_limit_price(current_price)

        data = {
            "price": limit_price,
            "volume": 0.1,
            "expiry_type": expiry_type,
            "stop_loss": OrderDataGenerator.calculate_stop_loss(limit_price),
            "take_profit": OrderDataGenerator.calculate_take_profit(limit_price),
            "order_datetime": datetime.now()
        }

        # Add expiry date for date-based expiry types
        if "Date" in expiry_type:
            data["expiry_date"] = OrderDataGenerator.generate_future_date()

        return data

    @staticmethod
    def generate_stop_order_data(current_price: float, expiry_type: str = "Good Till Canceled") -> Dict[str, Any]:
        """
        Generate complete stop order test data

        Args:
            current_price: Current market price
            expiry_type: Type of expiry

        Returns:
            Dictionary with order data
        """
        stop_price = OrderDataGenerator.calculate_stop_price(current_price)

        data = {
            "price": stop_price,
            "volume": 0.1,
            "expiry_type": expiry_type,
            "stop_loss": OrderDataGenerator.calculate_stop_loss(stop_price),
            "take_profit": OrderDataGenerator.calculate_take_profit(stop_price),
        }

        # Add expiry date for date-based expiry types
        if "Date" in expiry_type:
            data["expiry_date"] = OrderDataGenerator.generate_future_date()

        return data


class PriceCalculator:
    """Helper class for price calculations"""

    @staticmethod
    def calculate_percentage_change(original: float, percentage: float) -> float:
        """
        Calculate new price after percentage change

        Args:
            original: Original price
            percentage: Percentage change (positive or negative)

        Returns:
            New price
        """
        return round(original * (1 + percentage / 100), 5)

    @staticmethod
    def calculate_percentage_diff(price1: float, price2: float) -> float:
        """
        Calculate percentage difference between two prices

        Args:
            price1: First price
            price2: Second price

        Returns:
            Percentage difference
        """
        return round(((price2 - price1) / price1) * 100, 2)