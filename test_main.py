import re
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def browser_context(playwright):
    """Session-scoped browser context that persists across tests"""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Start tracing
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # Stop tracing and save
    context.tracing.stop(path="trace.zip")
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
    volume_input.fill("0.1")

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

def test_demo_editOpenPosition(authenticated_page: Page):
    #click on Assets tab to see all orders
    authenticated_page.get_by_test_id("side-bar-option-assets").click()

    #make sure both pending and open orders are present
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-open-positions")).to_be_visible()

    #retrieve the latest open position
    latestRow = authenticated_page.get_by_test_id("asset-open-list-item").last
    latestRow.get_by_test_id("asset-open-button-edit").click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_text("Edit Position")).to_be_visible(timeout=10000)
    expect(authenticated_page.get_by_test_id("edit-button-order")).to_be_visible(timeout=10000)
    
    # retrieve the stopLoss and takeProfit values
    currentStoplossPrice = authenticated_page.get_by_test_id("trade-input-stoploss-price").input_value()
    currentTakeprofitPrice = authenticated_page.get_by_test_id("trade-input-takeprofit-price").input_value()
    #for Debug purposes
    print(f"Current Stoploss Price: {currentStoplossPrice}  Current Takeprofit Price: {currentTakeprofitPrice}")

    #modify the stoploss and takeprofit prices by 3 % each
    newStoplossPrice = round(float(currentStoplossPrice)*0.97, 5)
    newTakeprofitPrice = round(float(currentTakeprofitPrice)*1.03, 5)
    print(f"New Stoploss Price: {newStoplossPrice}  New Takeprofit Price: {newTakeprofitPrice}")
    authenticated_page.get_by_test_id("trade-input-stoploss-price").fill(str(newStoplossPrice))
    authenticated_page.get_by_test_id("trade-input-takeprofit-price").fill(str(newTakeprofitPrice))
    #click on separate field to activate auto-update
    authenticated_page.get_by_test_id("trade-input-takeprofit-points").click()
    # click on update position button
    authenticated_page.get_by_test_id("edit-button-order").click()

    #expect order confirmation dialog to appear
    expect(authenticated_page.get_by_text("Order Confirmation")).to_be_visible(timeout=10000)
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)

    #Verify correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY")
    # verify the stopLoss and takeprofit price changes
    # Target the parent div that contains both label and value, then get the value sibling
    # basically 1 parent -> 1st div(label):text with stop loss, 2nd div(value):text
    stop_loss_value = authenticated_page.locator('[data-testid="trade-confirmation-label"]:has-text("Stop Loss") + [data-testid="trade-confirmation-value"]')
    take_profit_value = authenticated_page.locator('[data-testid="trade-confirmation-label"]:has-text("Take Profit") + [data-testid="trade-confirmation-value"]')

    # Wait for elements to be visible
    expect(stop_loss_value).to_be_visible()
    expect(take_profit_value).to_be_visible()

    tradeStopLossPrice = stop_loss_value.text_content()
    tradeTakeProfitPrice = take_profit_value.text_content()

    print(f"Trade Stop Loss: {tradeStopLossPrice}, Trade Take Profit: {tradeTakeProfitPrice}")
    if float(tradeStopLossPrice) != newStoplossPrice:
        raise AssertionError(f"Stop Loss price mismatch: expected {newStoplossPrice}, got {tradeStopLossPrice}")
    if float(tradeTakeProfitPrice) != newTakeprofitPrice:
        raise AssertionError(f"Take Profit price mismatch: expected {newTakeprofitPrice}, got {tradeTakeProfitPrice}")
    
    #click confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()

    #expect toast notification
    expect(authenticated_page.get_by_text("Position has been updated.")).to_be_visible()

def test_demo_partialCloseOpenPosition(authenticated_page: Page):
    #click on Assets tab to see all orders
    authenticated_page.get_by_test_id("side-bar-option-assets").click()

    #make sure both pending and open orders are present
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-open-positions")).to_be_visible()

    #retrieve the latest open position
    latestRow = authenticated_page.get_by_test_id("asset-open-list-item").last
    # click on the close button
    latestRow.get_by_test_id("asset-open-button-close").click()

    #expect Close confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_text("Confirm To Close Position")).to_be_visible(timeout=10000)
    expect(authenticated_page.get_by_role("button").get_by_text("Confirm")).to_be_visible(timeout=10000)

    #retrieve order number to confirm if full close later
    orderNumberList = authenticated_page.locator('div:has(div:text("Order No.")) + div').all()
    #To Debug
    for i, val in enumerate(orderNumberList):
        print(f"Order Number Element Text[{i}]: '{val.text_content()}'")
    orderNumber = orderNumberList[0].text_content()
    #retrieve current volume
    currentVolume = authenticated_page.get_by_placeholder("Min: 0.01").input_value()
    print(f"Current Volume: {currentVolume}")
    #calculate half volume
    halfVolume = round(float(currentVolume)/2, 5)
    print(f"Half Volume: {halfVolume}")
    # fill in half volume
    volume_input = authenticated_page.get_by_placeholder("Min: 0.01").fill(str(halfVolume))
    # click on confirm Close position button
    authenticated_page.get_by_role("button").get_by_text("Confirm").click()
    #expect toast notification
    expect(authenticated_page.get_by_text("Position has been closed.")).to_be_visible()

    #verfiy that the order number is still in the open positions list
    open_positions = authenticated_page.get_by_test_id("asset-open-list-item").all()
    for pos in open_positions:
        pos_text = pos.get_by_test_id("asset-open-column-order-id").text_content()
        if orderNumber in pos_text:
            print(f"Order Number {orderNumber} still found in open positions after partial close, as expected.")
            pos.get_by_test_id("asset-open-button-close").click()
            #check the remaing volume is equal to halfVolume
            remainingVolume = authenticated_page.get_by_placeholder("Min: 0.01").input_value()
            if float(remainingVolume) != halfVolume:
                raise AssertionError(f"Remaining volume mismatch: expected {halfVolume}, got {remainingVolume}")
            return
        else:
            raise AssertionError(f"Order Number {orderNumber} not found in open positions after partial close.")
        
def test_demo_fullCloseOpenPosition(authenticated_page: Page):
    #click on Assets tab to see all orders
    authenticated_page.get_by_test_id("side-bar-option-assets").click()

    #make sure both pending and open orders are present
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-open-positions")).to_be_visible()

    #retrieve the latest open position
    latestRow = authenticated_page.get_by_test_id("asset-open-list-item").last
    # click on the close button
    latestRow.get_by_test_id("asset-open-button-close").click()

    #expect Close confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_text("Confirm To Close Position")).to_be_visible(timeout=10000)
    expect(authenticated_page.get_by_role("button").get_by_text("Confirm")).to_be_visible(timeout=10000)

    #retrieve order number to confirm if full close later
    orderNumberList = authenticated_page.locator('div:has(div:text("Order No.")) + div').all()
    #To Debug
    for i, val in enumerate(orderNumberList):
        print(f"Order Number Element Text[{i}]: '{val.text_content()}'")
    orderNumber = orderNumberList[0].text_content()

    #max button to get full volume
    authenticated_page.get_by_test_id("close-order-input-volume-static-max").click()
    # click on confirm Close position button
    authenticated_page.get_by_role("button").get_by_text("Confirm").click()
    #expect toast notification
    expect(authenticated_page.get_by_text("Position has been closed.")).to_be_visible()
    #verfiy that the order number is no longer in the open positions list
    open_positions = authenticated_page.get_by_test_id("asset-open-list-item").all()
    for pos in open_positions:
        pos_text = pos.get_by_test_id("asset-open-column-order-id").text_content()
        if orderNumber in pos_text:
            raise AssertionError(f"Order Number {orderNumber} still found in open positions after closing.")

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

    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_vis

    #click on Assets tab to see all orders
    authenticated_page.get_by_test_id("side-bar-option-assets").click()

    #make sure both pending and open orders are present
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-open-positions")).to_be_visible()
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-pending-orders")).to_be_visible()