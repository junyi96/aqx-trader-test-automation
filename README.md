# Repository for Python Test Script to test Aqx Trade Page

This repository will be using the Playwright framework alongside Python to automate testing.

## Index
- [Pre-Requisite](#pre-requisite)
- [Place Market with Stop Loss and Take Profit](#place-Market-with-Stop-Loss-and-Take-Profit)  
- [Edit, partial close and close Open position](#edit,-partial-close-and-close-Open-position)  
- [Place Limit / Stop order with different types of Expiry](#place-Limit-/-Stop-order-with-different-types-of-Expiry)  
- [Edit Pending Orders for all values included](#edit-Pending-Orders-for-all-values-included)
- [Validate the order placed details with compare to notifications and position table details](#Validate-the-order-placed-details-with-compare-to-notifications-and-position-table-details)
- [Validate Order History data](#Validate-Order-History-data)
- [Room for Improvement](#room-for-improvement)

## Pre-Requisite

1. Install the python
2. Install the python Pytest plugin
```
pip install pytest-playwright
```
3. Install the required browsers
```
playwright install
```
4. Now run the pytest command in the folder via CMD or Bash
```
pytest
```

##  Place Market with Stop Loss and Take Profit

It has been completed with 
```
def test_demo_MarketOrder(page: Page):
```

### Comments
One of the more tedious issues with creating this test script was accounting for the auto create in fields such as the stop loss and take profit points that happen automatically.   Multiple simulated clicks had to be performed to ensure that the dynamic filling happens as intended.

##  Edit, partial close and close Open position
Created the module
`def test_demo_editOpenPosition`
to test the Edit Open Position.

`def test_demo_partialCloseOpenPosition`
will test the partial close position by closing half of volume out of the standard 0.1 used in the place market in the previous test script.

`def test_demo_fullCloseOpenPosition`
will test the Full close position using the max button

##  place Limit / Stop order with different types of Expiry

Multiple modules have been created for each type of expiry matching each Limit Order.

Below are the expected methods testing each order and type of Expiry
1. [x] Limit Order with "Good Til Canceled" Expiry : `test_demo_createLimitGoodTillCanceled`
2. [x] Limit Order with "Good Til Day" Expiry : `test_demo_createLimitGoodTillDay`
3. [x] Limit Order with "Good Til Specified Date" Expiry : `test_demo_createLimitGoodTillDate`
4. [x] Limit Order with "Good Til Specified Date and Time" Expiry : `test_demo_createLimitGoodTillDateAndTime`
5. [x] Stop Order with "Good Til Canceled" Expiry : `test_demo_createStopGoodTillCanceled`
6. [x] Stop Order with "Good Til Day" Expiry : `test_demo_createStopGoodTillDay`
7. [x] Stop Order with "Good Til Specified Date" Expiry : `test_demo_createStopGoodTillDate`
8. [x] Stop Order with "Good Til Specified Date and Time" Expiry : `test_demo_createStopGoodTillDateAndTime`

Note that the test script for specified date will have issues if the date is next month the program was using the aria-label to find the day to click.

TODO: 
1. Find a way to ensure that the test script for specified date can handle if the new date is on a different month.
2. Find a way to check if the specific created order was in the pending orders table as mentioned in the [final requirements](#Validate-the-order-placed-details-with-compare-to-notifications-and-position-table-details)

## Edit Pending Orders for all values included 

The edit test script is in `test_demo_editPendingOrder`.

## Validate the order placed details with compare to notifications and position table details

All the Orders placed are validated compared to notifications by default as seen in the expect() statment in the MarketOrder test Case and Stop/Limit Test Case.

## Validate Order History data 

The validate Order History Data is currently used in `test_demo_validateOrderHistory` test case.

## Room for Improvement

1. All the test cases are currently in 1 test file in `test_main.py` which is too cumbersome.
Refactoring will need to be done to separate the test cases into seprate files based on function such as the Order Creation and Order Edit.
2. The test trace is 1 per whole test script which makes debugging exponentially harder. 
The test script has to be modified to generate test trace per test case for better debugging.
3. Most of the test case use the same section of code. It may be prudent to find a way to decouple those code for better readability.
4. this is just 1 test script and not a full automation test framework.

## Critisms from the Tester

You created test scripts, but not a proper automation framework. The feedback isn't about JMeter (that's for performance testing) - it's about missing the fundamental structure and design patterns expected in a professional test automation framework.
What Was Missing: Full Automation Framework Components
1. Page Object Model (POM) - Critical Missing Component
You should have separated page interactions from test logic:

├── pages/
│   ├── base_page.py
│   ├── login_page.py
│   ├── trading_page.py
│   ├── assets_page.py
│   ├── order_confirmation_dialog.py
│   └── position_management_page.py
Example:

# pages/trading_page.py
class TradingPage:
    def __init__(self, page):
        self.page = page
        
    def place_market_order(self, volume, stop_loss, take_profit):
        """Encapsulates all market order logic"""
        self.page.get_by_test_id("trade-input-volume").fill(volume)
        # ... etc
        
    def get_current_buy_price(self):
        return self.page.get_by_test_id("trade-live-buy-price").text_content()
2. Configuration Management
Missing config/ directory:

├── config/
│   ├── config.py
│   ├── environments.yaml
│   └── test_data.json
Should handle:
Environment URLs (dev, staging, prod)
Test credentials (from env variables, not hardcoded)
Test data management
3. Utilities/Helpers
Missing utils/ directory:

├── utils/
│   ├── logger.py
│   ├── data_generator.py
│   ├── date_helpers.py
│   └── assertion_helpers.py
4. Test Data Management
Missing structured test data:

├── test_data/
│   ├── market_orders.json
│   ├── limit_orders.json
│   └── users.json
5. Reporting & Logging
Missing:
Proper logging setup (Python logging module)
Custom reporters
Screenshot capture on failure
Allure or similar reporting framework
6. CI/CD Integration
Missing:

├── .github/workflows/
│   └── test.yml
├── Dockerfile
└── docker-compose.yml
7. Project Structure
You only had 1 file. Should have been:

aqx-trader-test-automation/
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
│   ├── __init__.py
│   ├── config.py
│   └── environments.yaml
├── pages/
│   ├── __init__.py
│   ├── base_page.py
│   ├── login_page.py
│   ├── trading_page.py
│   └── assets_page.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_market_orders.py
│   ├── test_limit_orders.py
│   ├── test_stop_orders.py
│   └── test_position_management.py
├── test_data/
│   ├── orders.json
│   └── users.json
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── data_helpers.py
│   └── custom_assertions.py
├── reports/
├── screenshots/
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
├── README.md
└── Dockerfile
8. Design Patterns Missing
Factory Pattern for test data:

class OrderFactory:
    @staticmethod
    def create_market_order(**kwargs):
        return {
            "type": "MARKET",
            "volume": kwargs.get("volume", 0.1),
            ...
        }
Builder Pattern for complex orders:

order = OrderBuilder()
    .set_type("LIMIT")
    .set_volume(0.1)
    .set_expiry("GTC")
    .build()
9. Missing Testing Best Practices
No data-driven testing (parameterization)
No fixtures separation (conftest.py structure)
Hardcoded credentials (security issue)
No retry logic for flaky tests
No custom waits/conditions
No API testing layer (for setup/teardown)
10. Documentation Missing
Architecture documentation
Test strategy document
How to extend the framework
Troubleshooting guide
Contributing guidelines
What They Expected vs What You Delivered
Expected Framework Component	What You Had
Page Object Model	❌ All locators in test file
Modular test structure	❌ Single 1200-line file
Config management	❌ Hardcoded values
Data-driven tests	❌ Repetitive test code
Proper reporting	❌ Basic pytest output
CI/CD pipeline	❌ None
Logging framework	❌ Basic print statements
Reusable utilities	❌ Duplicated code
Professional structure	❌ Flat structure
"Lacks Sufficient Depth"
They saw:
Repetitive code - Same logic copy-pasted 14 times
No abstraction - Every test does low-level Playwright calls
No scalability - Adding new tests means copy-paste
No maintainability - Changing a locator means editing 50+ places
Beginner-level - Looked like someone following a tutorial, not building production code
What "Full Automation Framework" Means
It's not about JMeter. It means they wanted to see:
Architectural thinking - How you design scalable systems
Software engineering principles - DRY, SOLID, separation of concerns
Production-ready code - Not just "scripts that work"
Professional practices - Logging, reporting, CI/CD
Maintainability - Easy for other developers to extend
You delivered functional test scripts. They wanted a professional automation framework architecture. Would you like me to help you rebuild this into a proper automation framework structure? I can show you exactly how to refactor it to meet professional standards.

