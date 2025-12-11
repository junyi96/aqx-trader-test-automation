import re
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def browser_context(playwright):
    """Session-scoped browser context that persists across tests"""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    yield context
    context.close()
    browser.close()

@pytest.fixture(scope="session")
def authenticated_page(browser_context):
    """Session-scoped page with login performed once"""
    page = browser_context.new_page()
    
    # Perform login once
    page.goto("https://aqxtrader.aquariux.com")
    # Fill in the login form.
    page.get_by_test_id("login-user-id").fill("1000370")
    page.get_by_test_id("login-password").fill("FE4Pi$q5Syj$")
    
    #expect the login button to be enabled once the 2 form fields are filled
    expect(page.get_by_test_id("login-submit")).to_be_enabled()
    page.get_by_test_id("login-submit").click()
    # get span with id 0, the best i can do - wait up to 15 seconds for announcement after login
    announcements = page.locator('[id="0"]')
    expect(announcements).to_contain_text("Welcome to AQX Trader!", timeout=15000)
    #find the element with text Lay Jun Yi and confirm it is visible
    names = page.locator("text=Lay Jun Yi")
    expect(names).to_be_visible(timeout=10000)

    yield page
    page.close()

def test_demo_MarketOrder(authenticated_page: Page):
    #get current buy prices - wait for element to have actual price content
    price_element = authenticated_page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #prepare the price inputs as 5 % more and less than current price
    stopLossPrice = currentPrice*0.95
    takeProfitPrice = currentPrice*1.05
    authenticated_page.get_by_test_id("trade-input-stoploss-price").fill(str(stopLossPrice))
    authenticated_page.get_by_test_id("trade-input-takeprofit-price").fill(str(takeProfitPrice))

    #need to click on 2 different fields for the take profit points and volume points to auto-fill
    authenticated_page.get_by_test_id("trade-input-takeprofit-points").click()

    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.01")

    # add voume by 30 as min
    #page.get_by_test_id("trade-input-stoploss-points").fill("30")
    #page.get_by_test_id("trade-input-takeprofit-points").fill("30")

    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)

    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY")

    # place a market order
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()

    expect(authenticated_page.get_by_text("Position has been created")).to_be_visible()

def test_demo_editPendingOrder(authenticated_page: Page):
    #get current buy prices - wait for element to have actual price content
    price_element = authenticated_page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #Make the buyLowPrice 10 % less than current price.
    buyLowPrice = currentPrice*0.90

    #create a pending order first
    authenticated_page.get_by_test_id("trade-dropdown-order-type").select_option("Limit")

    authenticated_page.get_by_role("input", name="price").fill(str(buyLowPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.08")

    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)

    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY LIMIT")

    #click on Assets tab to see all orders
    authenticated_page.get_by_test_id("side-bar-option-assets").click()

    #make sure both pending and open orders are present
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-open-positions")).to_be_visible()
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-pending-orders")).to_be_visible()