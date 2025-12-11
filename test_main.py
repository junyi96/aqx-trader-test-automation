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

    # get span with id 0, the best i can do
    announcements = page.locator('[id="0"]')
    expect(announcements).to_contain_text("Welcome to AQX Trader!")
    #find the element with text Lay Jun Yi and confirm it is visible
    names = page.locator("text=Lay Jun Yi")
    expect(names).to_be_visible()

def test_demo_MarketOrder(page: Page):
    page.goto("https://aqxtrader.aquariux.com")

    # Fill in the login form.
    page.get_by_test_id("login-user-id").fill("1000370")
    page.get_by_test_id("login-password").fill("FE4Pi$q5Syj$")
    
    #expect the login button to be enabled once the 2 form fields are filled
    expect(page.get_by_test_id("login-submit")).to_be_enabled()
    page.get_by_test_id("login-submit").click()

    # get span with id 0, the best i can do
    announcements = page.locator('[id="0"]')
    expect(announcements).to_contain_text("Welcome to AQX Trader!")
    #find the element with text Lay Jun Yi and confirm it is visible
    names = page.locator("text=Lay Jun Yi")
    expect(names).to_be_visible()

    #get current buy prices
    currentPrice = page.get_by_test_id("trade-live-buy-price").text_content()
    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #prepare the price inputs as 5 % more and less than current price
    stopLossPrice = currentPrice*0.95
    takeProfitPrice = currentPrice*1.05
    page.get_by_test_id("trade-input-stoploss-price").fill(str(stopLossPrice))
    page.get_by_test_id("trade-input-takeprofit-price").fill(str(takeProfitPrice))

    # add voume by 30 as min
    #page.get_by_test_id("trade-input-stoploss-points").fill("30")
    #page.get_by_test_id("trade-input-takeprofit-points").fill("30")
    page.get_by_test_id("trade-button-order").click()

    #expect trade confirmation
    expect(page.get_by_role("div", id="overlay-aqx-trader"))
    # place a market order
    page.get_by_test_id("trade-confirmation-button-confirm").click()

    expect(page.get_by_text("Order placed successfully")).to_be_visible()