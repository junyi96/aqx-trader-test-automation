import re
import pytest
from playwright.sync_api import Page, expect

def test_demopage(page: Page):
    page.goto("https://aqxtrader.aquariux.com")

    # Expect a title "to be exactly" a string.
    expect(page).to_have_title("Aquariux - WebTrader Platform")

def test_demo_login(page: Page):
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

def test_demo_MarketOrder(page: Page):
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

    #get current buy prices - wait for element to have actual price content
    price_element = page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #prepare the price inputs as 5 % more and less than current price
    stopLossPrice = currentPrice*0.95
    takeProfitPrice = currentPrice*1.05
    page.get_by_test_id("trade-input-stoploss-price").fill(str(stopLossPrice))
    page.get_by_test_id("trade-input-takeprofit-price").fill(str(takeProfitPrice))

    #need to click on 2 different fields for the take profit points and volume points to auto-fill
    page.get_by_test_id("trade-input-takeprofit-points").click()

    # Clear and fill volume field
    volume_input = page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.01")

    # add voume by 30 as min
    #page.get_by_test_id("trade-input-stoploss-points").fill("30")
    #page.get_by_test_id("trade-input-takeprofit-points").fill("30")

    # Ensure the order button is enabled before clicking
    order_button = page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)

    # Verify confirmation dialog shows the correct order type
    expect(page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY")

    # place a market order
    page.get_by_test_id("trade-confirmation-button-confirm").click()

    expect(page.get_by_text("Position has been created")).to_be_visible()