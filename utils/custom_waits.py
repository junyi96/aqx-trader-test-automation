"""
Custom wait conditions and retry logic
"""
from playwright.sync_api import Page, Locator
from typing import Callable, Any
import time


class CustomWaits:
    """Custom wait conditions for specific scenarios"""

    @staticmethod
    def wait_for_input_value(
        locator: Locator,
        timeout: int = 10000,
        check_interval: int = 100
    ) -> str:
        """
        Wait for an input field to have a non-empty value

        Args:
            locator: The input element locator
            timeout: Maximum wait time in milliseconds
            check_interval: How often to check in milliseconds

        Returns:
            The input value

        Raises:
            TimeoutError: If value doesn't appear within timeout
        """
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout:
            value = locator.input_value()
            if value and value.strip():
                return value
            time.sleep(check_interval / 1000)

        raise TimeoutError(f"Input value not populated within {timeout}ms")

    @staticmethod
    def wait_for_numeric_value(
        locator: Locator,
        timeout: int = 10000,
        check_interval: int = 100
    ) -> float:
        """
        Wait for an input field to have a numeric value

        Args:
            locator: The input element locator
            timeout: Maximum wait time in milliseconds
            check_interval: How often to check in milliseconds

        Returns:
            The numeric value

        Raises:
            TimeoutError: If numeric value doesn't appear within timeout
        """
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout:
            value = locator.input_value()
            if value and value.strip():
                try:
                    return float(value)
                except ValueError:
                    pass
            time.sleep(check_interval / 1000)

        raise TimeoutError(f"Numeric value not populated within {timeout}ms")

    @staticmethod
    def wait_for_condition(
        condition: Callable[[], bool],
        timeout: int = 10000,
        check_interval: int = 100,
        error_message: str = "Condition not met within timeout"
    ):
        """
        Wait for a custom condition to be true

        Args:
            condition: Callable that returns True when condition is met
            timeout: Maximum wait time in milliseconds
            check_interval: How often to check in milliseconds
            error_message: Error message if timeout occurs

        Raises:
            TimeoutError: If condition not met within timeout
        """
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout:
            if condition():
                return
            time.sleep(check_interval / 1000)

        raise TimeoutError(f"{error_message} ({timeout}ms)")

    @staticmethod
    def wait_for_element_count(
        page: Page,
        selector: str,
        expected_count: int,
        timeout: int = 10000,
        check_interval: int = 100
    ):
        """
        Wait for a specific number of elements matching a selector

        Args:
            page: Playwright page object
            selector: Element selector
            expected_count: Expected number of elements
            timeout: Maximum wait time in milliseconds
            check_interval: How often to check in milliseconds

        Raises:
            TimeoutError: If expected count not reached within timeout
        """
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout:
            count = page.locator(selector).count()
            if count == expected_count:
                return
            time.sleep(check_interval / 1000)

        raise TimeoutError(
            f"Expected {expected_count} elements, but count didn't match within {timeout}ms"
        )


class RetryHelper:
    """Helper for retrying operations"""

    @staticmethod
    def retry_on_exception(
        func: Callable,
        max_attempts: int = 3,
        delay: int = 1000,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Retry a function on exception

        Args:
            func: Function to retry
            max_attempts: Maximum number of attempts
            delay: Delay between attempts in milliseconds
            exceptions: Tuple of exceptions to catch

        Returns:
            Result of successful function call

        Raises:
            Last exception if all attempts fail
        """
        last_exception = None

        for attempt in range(max_attempts):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    time.sleep(delay / 1000)
                    continue
                else:
                    raise last_exception