# Repository for Python Test Script to test Aqx Trade Page

This repository will be using the Playwright framework alongside Python to automate testing.

## Index
[place Market with Stop Loss and Take Profit](place-Market-with-Stop-Loss-and-Take-Profit)  
[Edit, partial close and close Open position](edit,-partial-close-and-close-Open-position)  
[Place Limit / Stop order with different types of Expiry](place-Limit-/-Stop-order-with-different-types-of-Expiry)  
[Edit Pending Orders for all values included](edit-Pending-Orders-for-all-values-included)
[Validate the order placed details with compare to notifications and position table details](Validate-the-order-placed-details-with-compare-to-notifications-and-position-table-details)
[Validate Order History data](Validate-Order-History-data)

##  place Market with Stop Loss and Take Profit

It has been completed with 
```
def test_demo_MarketOrder(page: Page):
```

### Comments
One of the more tedious issues with creating this test script was accounting for the auto create in fields such as the stop loss and take profit points that happen automatically.   Multiple simulated clicks had to be performed to ensure that the dynamic filling happens as intended.
##  Edit, partial close and close Open position

##  place Limit / Stop order with different types of Expiry

## edit Pending Orders for all values included 

## Validate the order placed details with compare to notifications and position table details

## Validate Order History data 