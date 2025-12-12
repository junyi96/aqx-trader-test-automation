import re
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta

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

@pytest.fixture(autouse=True)
def log_test_boundary(request):
    """Automatically log test start/end for better trace readability"""
    test_name = request.node.name
    print("\n" + "="*80)
    print(f"STARTING TEST: {test_name}")
    print("="*80 + "\n")
    
    yield
    
    print("\n" + "="*80)
    print(f"FINISHED TEST: {test_name}")
    print("="*80 + "\n")

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
    # go to assets tab page
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/assets")
    #click on Assets tab to see all orders
    #authenticated_page.get_by_test_id("side-bar-option-assets").click()

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

    #modify the stoploss and takeprofit prices by 5 % each
    newStoplossPrice = round(float(currentStoplossPrice)*0.95, 5)
    newTakeprofitPrice = round(float(currentTakeprofitPrice)*1.05, 5)
    print(f"New Stoploss Price: {newStoplossPrice}  New Takeprofit Price: {newTakeprofitPrice}")
    authenticated_page.get_by_test_id("trade-input-stoploss-price").fill(str(newStoplossPrice))
    authenticated_page.get_by_test_id("trade-input-stoploss-points").click()  #click on separate field to activate auto-update
    expect(authenticated_page.get_by_test_id("trade-input-stoploss-price")).to_have_value(str(newStoplossPrice))
    authenticated_page.get_by_test_id("trade-input-takeprofit-price").fill(str(newTakeprofitPrice))
    authenticated_page.get_by_test_id("trade-input-stoploss-points").click()  #click on separate field to activate auto-update
    expect(authenticated_page.get_by_test_id("trade-input-takeprofit-price")).to_have_value(str(newTakeprofitPrice))

    authenticated_page.get_by_test_id("trade-input-stoploss-points").click()
    authenticated_page.get_by_test_id("trade-input-takeprofit-points").click()
    expect(authenticated_page.get_by_test_id("trade-input-stoploss-points")).not_to_be_empty(timeout=5000)
    expect(authenticated_page.get_by_test_id("trade-input-takeprofit-points")).not_to_be_empty(timeout=5000)
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
    stop_loss_value = authenticated_page.locator('div[data-testid="trade-confirmation-label"]:has-text("Stop Loss") + div[data-testid="trade-confirmation-value"]')
    take_profit_value = authenticated_page.locator('div[data-testid="trade-confirmation-label"]:has-text("Take Profit") + div[data-testid="trade-confirmation-value"]')

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
    # go to assets tab page
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/assets")
    #click on Assets tab to see all orders
    #authenticated_page.get_by_test_id("side-bar-option-assets").click()

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
    overlay = authenticated_page.locator('div[id="overlay-aqx-trader"]')
    orderNumberList = overlay.locator('div:has-text("Order No.") + div').first
    #To Debug
    orderNumber = orderNumberList.text_content()
    print(f"Order Number Element Text : '{orderNumber}'")
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

    #wait for the open positions list to refresh
    authenticated_page.wait_for_timeout(4000)
    #verfiy that the order number is still in the open positions list
    open_positions = authenticated_page.get_by_test_id("asset-open-list-item").all()
    found = False
    for pos in open_positions:
        pos_text = pos.get_by_test_id("asset-open-column-order-id").text_content()
        print(f"Checking open position Order ID: '{pos_text}' against '{orderNumber}'")
        if orderNumber in pos_text:
            print(f"Order Number {orderNumber} still found in open positions after partial close, as expected.")
            pos.get_by_test_id("asset-open-button-close").click()
            #check the remaing volume is equal to halfVolume
            remainingVolume = authenticated_page.get_by_placeholder("Min: 0.01").input_value()
            found = True
            if float(remainingVolume) != halfVolume:
                raise AssertionError(f"Remaining volume mismatch: expected {halfVolume}, got {remainingVolume}")
            break
    if not found:
        raise AssertionError(f"Order Number {orderNumber} not found in open positions after partial close.")
    
            
def test_demo_fullCloseOpenPosition(authenticated_page: Page):
    # go to assets tab page
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/assets")
    #click on Assets tab to see all orders
    # authenticated_page.get_by_test_id("side-bar-option-assets").click()

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

#the Limit Buy Order with Good Till Canceled expiry is pending order to buy when prices reach below stated price
def test_demo_createLimitGoodTillCanceled(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

    #get current buy prices - wait for element to have actual price content
    price_element = authenticated_page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #Make the buyLowPrice 10% less than current price.
    buyLowPrice = currentPrice*0.90

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Limit" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Limit", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(buyLowPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Canceled
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Canceled" option (note that this option is in a separate div element)
    #the second element has to be selected.
    authenticated_page.get_by_text("Good Till Canceled", exact=True).all()[1].click()
    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY LIMIT")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

#the Limit Buy Order with Good Till Day expiry is pending order to buy when prices reach below stated price 
# until day ends 
def test_demo_createLimitGoodTillDay(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

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

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Limit" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Limit", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(buyLowPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Day
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Day" option, note that default is Good Til Canceled and so no need for [1]. but note in future.
    authenticated_page.get_by_text("Good Till Day", exact=True).click()

    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY LIMIT")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

#the Limit Buy Order with Good Till Date expiry is pending order to buy when prices reach below stated price 
# until the spcified date
def test_demo_createLimitGoodTillDate(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

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

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Limit" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Limit", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(buyLowPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Day
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Day" option, note that default is Good Til Canceled and so no need for [1]. but note in future.
    authenticated_page.get_by_text("Specified Date", exact=True).click()

    # Calculate target date (7 days from now)
    future_date = datetime.now() + timedelta(days=7)
    print(f"Setting expiry date to: {future_date.strftime('%Y-%m-%d')}")

    # Click to open the react-calendar date picker
    authenticated_page.get_by_test_id("trade-input-expiry-date").click()

    # Wait for the calendar to appear
    authenticated_page.wait_for_selector('.react-calendar', timeout=5000)

    # Click the specific day using aria-label (format: "Month Day, Year")
    # Example: "December 19, 2025"
    target_aria_label = future_date.strftime("%B %d, %Y")  # "December 19, 2025"
    print(f"Looking for calendar day with aria-label: {target_aria_label}")

    # Find and click the button containing the abbr with the matching aria-label
    # Clicking the abbr element will trigger the parent button
    day_button = authenticated_page.locator(f'.react-calendar abbr[aria-label="{target_aria_label}"]')
    day_button.click()
    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY LIMIT")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

#the Limit Buy Order with Good Till Date expiry is pending order to buy when prices reach below stated price 
# until the spcified date
def test_demo_createLimitGoodTillDateAndTime(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

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

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Limit" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Limit", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(buyLowPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Day
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Day" option, note that default is Good Til Canceled and so no need for [1]. but note in future.
    authenticated_page.get_by_text("Specified Date and Time", exact=True).click()

    # Calculate target date (7 days from now)
    future_date = datetime.now() + timedelta(days=7)
    print(f"Setting expiry date & time to: {future_date.strftime('%Y-%m-%d %H:%M')}")

    # Click to open the react-calendar date picker
    authenticated_page.get_by_test_id("trade-input-expiry-date").click()

    # Wait for the calendar to appear
    authenticated_page.wait_for_selector('.react-calendar', timeout=5000)

    # Click the specific day using aria-label (format: "Month Day, Year")
    # Example: "December 19, 2025"
    target_aria_label = future_date.strftime("%B %d, %Y")  # "December 19, 2025"
    print(f"Looking for calendar day with aria-label: {target_aria_label}")

    # Find and click the button containing the abbr with the matching aria-label
    # Clicking the abbr element will trigger the parent button
    day_button = authenticated_page.locator(f'.react-calendar abbr[aria-label="{target_aria_label}"]')
    day_button.click()

    # Set the time picker
    target_hour = future_date.strftime("%H")  # 24-hour format with leading zero, e.g., "14"
    target_minute = future_date.strftime("%M")  # Minutes with leading zero, e.g., "05"

    print(f"Setting time to: {target_hour}:{target_minute}")

    # Click to open the time picker
    authenticated_page.get_by_test_id("trade-input-expiry-time").click()
    authenticated_page.wait_for_timeout(500)  # Wait for picker to render

    # Set Hour - click the Hour dropdown
    hour_dropdown = authenticated_page.locator('div:has-text("Hour") + div').first
    hour_dropdown.click()

    # Wait for the dropdown options to appear
    authenticated_page.wait_for_selector('[data-testid="options"]', timeout=5000)

    # Click the target hour from the dropdown
    authenticated_page.locator(f'[data-testid="options"] div:has-text("{target_hour}")').first.click()

    # Set Minute - click the Minute dropdown
    minute_dropdown = authenticated_page.locator('div:has-text("Minute") + div').first
    minute_dropdown.click()

    # Wait for the dropdown options to appear
    authenticated_page.wait_for_selector('[data-testid="options"]', timeout=5000)

    # Click the target minute from the dropdown
    authenticated_page.locator(f'[data-testid="options"] div:has-text("{target_minute}")').first.click()

    # Click OK to confirm the time
    authenticated_page.get_by_role("button", name="OK").click()

    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY LIMIT")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

#the Stop Buy Order with Good Till Canceled expiry is pending order to buy when prices reach above stated price
#to buy on a breakout
def test_demo_createStopGoodTillCanceled(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

    #get current buy prices - wait for element to have actual price content
    price_element = authenticated_page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #The breakoutPrice is the estimated threshold when buying momentum will increase
    # this threshold should be 2-5 % above current price, i will use 4
    breakoutPrice = currentPrice*1.04

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Stop" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Stop", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(breakoutPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Canceled
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Canceled" option (note that this option is in a separate div element)
    #the second element has to be selected.
    authenticated_page.get_by_text("Good Till Canceled", exact=True).all()[1].click()
    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type, buy stop in this case
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY STOP")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

#the Stop Buy Order with Good Till Day expiry is pending order to buy when prices reach above stated price 
# before day ends as part of a breakout/ buying momentum 
def test_demo_createStopGoodTillDay(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

    #get current buy prices - wait for element to have actual price content
    price_element = authenticated_page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #breakoutPrice 4 % more than current price.
    breakoutPrice = currentPrice*1.04

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Limit" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Stop", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(breakoutPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Day
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Day" option, note that default is Good Til Canceled and so no need for [1]. but note in future.
    authenticated_page.get_by_text("Good Till Day", exact=True).click()

    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY STOP")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

#Create Stop Buy Order with Good Till Date expiry is pending order to buy 
#when prices reach above stated price
def test_demo_createStopGoodTillDate(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

    #get current buy prices - wait for element to have actual price content
    price_element = authenticated_page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #breakoutPrice is 4 % less than current price.
    breakoutPrice = currentPrice*1.04

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Limit" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Stop", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(breakoutPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Day
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Day" option, note that default is Good Til Canceled and so no need for [1]. but note in future.
    authenticated_page.get_by_text("Specified Date", exact=True).click()

    # Calculate target date (7 days from now)
    future_date = datetime.now() + timedelta(days=7)
    print(f"Setting expiry date to: {future_date.strftime('%Y-%m-%d')}")

    # Click to open the react-calendar date picker
    authenticated_page.get_by_test_id("trade-input-expiry-date").click()

    # Wait for the calendar to appear
    authenticated_page.wait_for_selector('.react-calendar', timeout=5000)

    # Click the specific day using aria-label (format: "Month Day, Year")
    # Example: "December 19, 2025"
    target_aria_label = future_date.strftime("%B %d, %Y")  # "December 19, 2025"
    print(f"Looking for calendar day with aria-label: {target_aria_label}")

    # Find and click the button containing the abbr with the matching aria-label
    # Clicking the abbr element will trigger the parent button
    day_button = authenticated_page.locator(f'.react-calendar abbr[aria-label="{target_aria_label}"]')
    day_button.click()
    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY STOP")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

#the Stop Buy Order with Good Till Date expiry is pending order to buy when prices reach below stated price 
# until the spcified date
def test_demo_createStopGoodTillDateAndTime(authenticated_page: Page):
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")

    #get current buy prices - wait for element to have actual price content
    price_element = authenticated_page.get_by_test_id("trade-live-buy-price")

    # Wait for the price to actually contain numbers (not just be visible)
    expect(price_element).to_have_text(re.compile(r'\d+'), timeout=10000)

    currentPrice = price_element.text_content()
    # Debug: print what we got
    print(f"Raw price text: '{currentPrice}'")

    currentPrice = float(re.sub(r'[^\d.]', '', currentPrice))  #remove any non-numeric characters
    #breakout pricemore than 4% current price.
    breakoutPrice = currentPrice*1.04

    #create a pending order now with the new price
    # Click to open the dropdown (it's a custom div dropdown, not a native select)
    authenticated_page.get_by_test_id("trade-dropdown-order-type").click()

    # Click the "Limit" option from the opened dropdown menu (using text only, avoiding auto-generated classes)
    authenticated_page.get_by_text("Stop", exact=True).click()

    # Fill the price input field (name attribute is "price")
    price_input = authenticated_page.locator('input[name="price"]')
    expect(price_input).to_be_visible()
    price_input.fill(str(breakoutPrice))
    
    # Clear and fill volume field
    volume_input = authenticated_page.get_by_test_id("trade-input-volume")
    volume_input.click()
    volume_input.clear()
    volume_input.fill("0.1")

    # ensure order expiry is set to Good Till Day
    # Click to open the expiry dropdown (also a custom div dropdown)
    authenticated_page.get_by_test_id("trade-dropdown-expiry").click()

    # Click the "Good Till Day" option, note that default is Good Til Canceled and so no need for [1]. but note in future.
    authenticated_page.get_by_text("Specified Date and Time", exact=True).click()

    # Calculate target date (7 days from now)
    future_date = datetime.now() + timedelta(days=7)
    print(f"Setting expiry date & time to: {future_date.strftime('%Y-%m-%d %H:%M')}")

    # Click to open the react-calendar date picker
    authenticated_page.get_by_test_id("trade-input-expiry-date").click()

    # Wait for the calendar to appear
    authenticated_page.wait_for_selector('.react-calendar', timeout=5000)

    # Click the specific day using aria-label (format: "Month Day, Year")
    # Example: "December 19, 2025"
    target_aria_label = future_date.strftime("%B %d, %Y")  # "December 19, 2025"
    print(f"Looking for calendar day with aria-label: {target_aria_label}")

    # Find and click the button containing the abbr with the matching aria-label
    # Clicking the abbr element will trigger the parent button
    day_button = authenticated_page.locator(f'.react-calendar abbr[aria-label="{target_aria_label}"]')
    day_button.click()

    # Set the time picker
    target_hour = future_date.strftime("%H")  # 24-hour format with leading zero, e.g., "14"
    target_minute = future_date.strftime("%M")  # Minutes with leading zero, e.g., "05"

    print(f"Setting time to: {target_hour}:{target_minute}")

    # Click to open the time picker
    authenticated_page.get_by_test_id("trade-input-expiry-time").click()
    authenticated_page.wait_for_timeout(500)  # Wait for picker to render

    # Set Hour - click the Hour dropdown
    hour_dropdown = authenticated_page.locator('div:has-text("Hour") + div').first
    hour_dropdown.click()

    # Wait for the dropdown options to appear
    authenticated_page.wait_for_selector('[data-testid="options"]', timeout=5000)

    # Click the target hour from the dropdown
    authenticated_page.locator(f'[data-testid="options"] div:has-text("{target_hour}")').first.click()

    # Set Minute - click the Minute dropdown
    minute_dropdown = authenticated_page.locator('div:has-text("Minute") + div').first
    minute_dropdown.click()

    # Wait for the dropdown options to appear
    authenticated_page.wait_for_selector('[data-testid="options"]', timeout=5000)

    # Click the target minute from the dropdown
    authenticated_page.locator(f'[data-testid="options"] div:has-text("{target_minute}")').first.click()

    # Click OK to confirm the time
    authenticated_page.get_by_role("button", name="OK").click()

    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)
    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY STOP")

    #click on confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()
    #confirm toast notification
    expect(authenticated_page.get_by_text("Order has been created.")).to_be_visible(timeout=10000)

def test_demo_editPendingOrder(authenticated_page: Page):
    #Go to Assets page
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/assets")
    #click on Assets tab to see all orders
    #authenticated_page.get_by_test_id("side-bar-option-assets").click()

    #make sure both pending and open orders are present
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-open-positions")).to_be_visible()
    expect(authenticated_page.get_by_test_id("tab-asset-order-type-pending-orders")).to_be_visible()

    #click on Pending orders tab
    authenticated_page.get_by_test_id("tab-asset-order-type-pending-orders").click()
    
    #retrieve the latest pending position
    latestRow = authenticated_page.get_by_test_id("asset-pending-list-item").last
    latestRow.get_by_test_id("asset-open-button-edit").click()

    #locate the overlay dialog
    overlay = authenticated_page.locator('div[id="overlay-aqx-trader"]').all()[0]

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_text("Edit Order")).to_be_visible(timeout=10000)
    expect(overlay.locator('button:has-text("Confirm")')).to_be_visible(timeout=10000)
    
    # retrieve the orderPrice
    orderPrice = authenticated_page.locator('input[name="price"]').input_value()
    #for Debug purposes
    print(f"Current Order Price: {orderPrice}")

    orderLimitTypeList = overlay.locator('div').filter(has_text=re.compile(r"^BUY LIMIT$")).all()
    for element in orderLimitTypeList:
        print(f"BUY LIMIT elements found: {element.text_content()}")
    orderStopTypeList = overlay.locator('div').filter(has_text=re.compile(r"^BUY STOP$")).all()
    for element in orderStopTypeList:
        print(f"BUY STOP elements found: {element.text_content()}")

    # check if the order being edited is STOP or LIMIT
    #modify the orderPrice prices by 1 % up or down based on type of order
    if overlay.locator('div').filter(has_text=re.compile(r"^BUY LIMIT$")).all()[0].is_visible():
        # LIMIT order - reduce price by 0.5 % as limit order buys when stock price below stated price
        newOrderPrice = round(float(orderPrice)*0.995, 5)
        orderType = "BUY LIMIT"
    elif overlay.locator('div').filter(has_text=re.compile(r"^BUY STOP$")).all()[0].is_visible():
        # STOP order - increase price by 1 % as stop order buys when stock price above stated price
        newOrderPrice = round(float(orderPrice)*1.005, 5)
        orderType = "BUY STOP"
    
    print(f"New Order Price: {newOrderPrice}")
    #prepare the price inputs as 5 % more and less than current price
    stopLossPrice = round(newOrderPrice*0.95, 5)
    takeProfitPrice = round(newOrderPrice*1.05, 5)

    # new stoploss and takeprofit prices for verification later
    #note that the price input has to be first before the other 2 prices
    authenticated_page.locator('input[name="price"]').fill(str(newOrderPrice))
    authenticated_page.get_by_test_id("trade-input-stoploss-price").fill(str(stopLossPrice))
    authenticated_page.get_by_test_id("trade-input-takeprofit-price").fill(str(takeProfitPrice))
    

    #prepare future datetime in case of expiry change
    future_date = datetime.now() + timedelta(days=7)
    oldExpiryType: str = ""
    newExpiryType: str = ""
    #new Expiry Change
    expiryType = authenticated_page.get_by_test_id("trade-dropdown-expiry")
    if expiryType.get_by_text("Good Till Canceled").is_visible():
        oldExpiryType = "Good Till Canceled"
        newExpiryType = "Good Till Day"
        #change to Good Till Day
        expiryType.click()
        overlay.get_by_text("Good Till Day", exact=True).click()
        expect(overlay.get_by_test_id("trade-dropdown-expiry")).to_have_text(newExpiryType)
    elif expiryType.get_by_text("Good Till Day").is_visible():
        oldExpiryType = "Good Till Day"
        newExpiryType = "Specified Date"
        #change to Specified Date
        expiryType.click()
        overlay.get_by_text("Specified Date", exact=True).click()
        # Calculate target date (7 days from now)
        print(f"Setting expiry date to: {future_date.strftime('%Y-%m-%d')}")

        # Click to open the react-calendar date picker
        authenticated_page.get_by_test_id("trade-input-expiry-date").click()

        # Wait for the calendar to appear
        authenticated_page.wait_for_selector('.react-calendar', timeout=5000)

        # Click the specific day using aria-label (format: "Month Day, Year")
        # Example: "December 19, 2025"
        target_aria_label = future_date.strftime("%B %d, %Y")  # "December 19, 2025"
        print(f"Looking for calendar day with aria-label: {target_aria_label}")

        # Find and click the button containing the abbr with the matching aria-label
        # Clicking the abbr element will trigger the parent button
        day_button = authenticated_page.locator(f'.react-calendar abbr[aria-label="{target_aria_label}"]')
        day_button.click()
        expect(overlay.get_by_test_id("trade-dropdown-expiry")).to_have_text(newExpiryType)
    elif expiryType.get_by_text("Specified Date").is_visible():
        oldExpiryType = "Specified Date"
        newExpiryType = "Specified Date and Time"
        #change to Specified Date and Time
        expiryType.click()
        overlay.get_by_text("Specified Date and Time", exact=True).click()
        # Calculate target date (7 days from now)
        print(f"Setting expiry date & time to: {future_date.strftime('%Y-%m-%d %H:%M')}")

        # Click to open the react-calendar date picker
        authenticated_page.get_by_test_id("trade-input-expiry-date").click()

        # Wait for the calendar to appear
        authenticated_page.wait_for_selector('.react-calendar', timeout=5000)

        # Click the specific day using aria-label (format: "Month Day, Year")
        # Example: "December 19, 2025"
        target_aria_label = future_date.strftime("%B %d, %Y")  # "December 19, 2025"
        print(f"Looking for calendar day with aria-label: {target_aria_label}")

        # Find and click the button containing the abbr with the matching aria-label
        # Clicking the abbr element will trigger the parent button
        day_button = authenticated_page.locator(f'.react-calendar abbr[aria-label="{target_aria_label}"]')
        day_button.click()

        # Set the time picker
        target_hour = future_date.strftime("%H")  # 24-hour format with leading zero, e.g., "14"
        target_minute = future_date.strftime("%M")  # Minutes with leading zero, e.g., "05"

        print(f"Setting time to: {target_hour}:{target_minute}")

        # Click to open the time picker
        authenticated_page.get_by_test_id("trade-input-expiry-time").click()
        authenticated_page.wait_for_timeout(500)  # Wait for picker to render

        # Set Hour - click the Hour dropdown
        hour_dropdown = authenticated_page.locator('div:has-text("Hour") + div').first
        hour_dropdown.click()

        # Wait for the dropdown options to appear
        authenticated_page.wait_for_selector('[data-testid="options"]', timeout=5000)

        # Click the target hour from the dropdown
        authenticated_page.locator(f'[data-testid="options"] div:has-text("{target_hour}")').first.click()

        # Set Minute - click the Minute dropdown
        minute_dropdown = authenticated_page.locator('div:has-text("Minute") + div').first
        minute_dropdown.click()
        expect(overlay.get_by_test_id("trade-dropdown-expiry")).to_have_text(newExpiryType)
    elif expiryType.get_by_text("Specified Date and Time").is_visible():
        oldExpiryType = "Specified Date and Time"
        newExpiryType = "Good Till Canceled"
        #change to Good Till Canceled
        expiryType.click()
        overlay.get_by_text("Good Till Canceled", exact=True).click()
        expect(overlay.get_by_test_id("trade-dropdown-expiry")).to_have_text(newExpiryType)
    else:
        print("Expiry type not recognized, no changes made.")
        raise AssertionError("Expiry type not recognized, no changes made.")

    #Debug
    print(f"Old Expiry Type: {oldExpiryType}, New Expiry Type: {newExpiryType}")
    #click on separate field to activate auto-update
    authenticated_page.get_by_test_id("trade-input-takeprofit-points").click()


    # click on Confirm position button
    overlay.get_by_role("button").filter(has_text="Confirm").click()

    #expect order confirmation dialog to appear
    expect(overlay.get_by_text("Order Confirmation")).to_be_visible(timeout=10000)
    expect(overlay.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)

    #Verify correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text(orderType)
    #verify expiry type change
    #Debug
    confirmationValuesList = authenticated_page.locator('div[data-testid="trade-confirmation-value"]').all()
    # 0 is volume, 1 is units, 2 is price, 3 is stop loss, 4 is take profit, 5 is expiry, 6 is expirydate, 7 is Fill Policy
    expiryConfirmationValue = confirmationValuesList[5]
    print(f"Expiry Confirmation Value: {expiryConfirmationValue.text_content()}")
    expect(expiryConfirmationValue).to_have_text(newExpiryType)
    # verify the stopLoss and takeprofit price changes
    # Target the parent div that contains both label and value, then get the value sibling
    # basically 1 parent -> 1st div(label):text with stop loss, 2nd div(value):text
    stop_loss_value = confirmationValuesList[3]
    take_profit_value = confirmationValuesList[4]

    # Wait for elements to be visible
    expect(stop_loss_value).to_be_visible()
    expect(take_profit_value).to_be_visible()

    tradeStopLossPrice = stop_loss_value.text_content()
    tradeTakeProfitPrice = take_profit_value.text_content()

    print(f"Trade Stop Loss: {tradeStopLossPrice}, Trade Take Profit: {tradeTakeProfitPrice}")
    if float(tradeStopLossPrice) != stopLossPrice:
        raise AssertionError(f"Stop Loss price mismatch: expected {stopLossPrice}, got {tradeStopLossPrice}")
    if float(tradeTakeProfitPrice) != takeProfitPrice:
        raise AssertionError(f"Take Profit price mismatch: expected {takeProfitPrice}, got {tradeTakeProfitPrice}")
    
    #click confirm button
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()

    #expect toast notification
    expect(authenticated_page.get_by_text("Order has been updated.")).to_be_visible()

def test_demo_validateOrderHistory(authenticated_page: Page):
    # go to trade page
    authenticated_page.goto("https://aqxtrader.aquariux.com/web/trade")
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

    #get server time for order time verification later
    # retrieve server time e.g. Server Time : 2025-12-12 16:53:20
    server_time_str = authenticated_page.locator("div").filter(has_text=re.compile(r"^Server Time : ")).first.text_content()
    serverTime = server_time_str.replace("Server Time : ", "").strip()
    #convert to datetime
    serverTime_dt = datetime.strptime(serverTime, "%Y-%m-%d %H:%M:%S")

    # Ensure the order button is enabled before clicking
    order_button = authenticated_page.get_by_test_id("trade-button-order")
    expect(order_button).to_be_enabled()
    order_button.click()

    #expect trade confirmation dialog to appear - wait longer and check for the confirm button
    expect(authenticated_page.get_by_test_id("trade-confirmation-button-confirm")).to_be_visible(timeout=10000)

    # Verify confirmation dialog shows the correct order type
    expect(authenticated_page.get_by_test_id("trade-confirmation-order-type")).to_have_text("BUY")

    print(f"Server Time: {serverTime_dt}")
    # place a market order
    authenticated_page.get_by_test_id("trade-confirmation-button-confirm").click()

    expect(authenticated_page.get_by_text("Position has been created")).to_be_visible()

    #click on Assets tab to see all orders
    authenticated_page.get_by_test_id("side-bar-option-assets").click()
    #click on Postition History tab to go to order history
    authenticated_page.get_by_test_id("tab-asset-order-type-history").click()
    authenticated_page.get_by_test_id("tab-asset-order-type-history-orders-and-deals").click()
    
    smallest_time_diff = timedelta.max
    correctRow = None
    #wait for 2 seconds to ensure data loaded
    authenticated_page.wait_for_timeout(2000)
    #retrieve the latest pending position
    latestRow = authenticated_page.get_by_test_id("asset-history-position-list-item").all()
    for row in latestRow:
        row_dt_str = row.get_by_test_id("asset-history-column-open-date").text_content()
        row_dt = datetime.strptime(row_dt_str, "%Y-%m-%d %H:%M:%S")
        time_diff = abs(serverTime_dt - row_dt)
        if time_diff < smallest_time_diff:
            smallest_time_diff = time_diff
            correctRow = row
    orderNo = correctRow.get_by_test_id("asset-history-column-order-id").text_content()
    correctRow.get_by_test_id("asset-history-position-list-item-expand").click()