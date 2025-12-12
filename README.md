# Repository for Python Test Script to test Aqx Trade Page

This repository will be using the Playwright framework alongside Python to automate testing.

## Index
- [place Market with Stop Loss and Take Profit](#place-Market-with-Stop-Loss-and-Take-Profit)  
- [Edit, partial close and close Open position](#edit,-partial-close-and-close-Open-position)  
- [Place Limit / Stop order with different types of Expiry](#place-Limit-/-Stop-order-with-different-types-of-Expiry)  
- [Edit Pending Orders for all values included](#edit-Pending-Orders-for-all-values-included)
- [Validate the order placed details with compare to notifications and position table details](#Validate-the-order-placed-details-with-compare-to-notifications-and-position-table-details)
- [Validate Order History data](#Validate-Order-History-data)

##  place Market with Stop Loss and Take Profit

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
1. [x] Limit Order with "Good Til Canceled" Expiry 
2. [x] Limit Order with "Good Til Day" Expiry 
3. [x] Limit Order with "Good Til Specified Date" Expiry 
4. [x] Limit Order with "Good Til Specified Date and Time" Expiry 
5. [ ] Stop Order with "Good Til Canceled" Expiry 
6. [ ] Stop Order with "Good Til Day" Expiry 
7. [ ] Stop Order with "Good Til Specified Date" Expiry 
8. [ ] Stop Order with "Good Til Specified Date and Time" Expiry

Note that the test script for specified date will have issues if the date is next month the program was using the aria-label to find the day to click.

TODO: Find a way to check if the specific created order was in the pending orders table as mentioned in the [final requirements](#Validate-the-order-placed-details-with-compare-to-notifications-and-position-table-details)

## edit Pending Orders for all values included 

## Validate the order placed details with compare to notifications and position table details

## Validate Order History data 