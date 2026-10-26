# Adjust Inventory case flow

## Exact buyer flow used by automation

1. Log in as buyeruser.
2. Open the Actions page.
3. Open Adjust Inventory.
4. Select any item.
5. Click Show Cards.
6. Select two cards.
7. Enter Adjust Qty = 100.
8. Enter a random Current Location.
9. Click Adjust Inventory.

## Notes

- This is the minimal flow required by the user and kept in the Selenium automation.
- The automation waits for the item list to load and handles the filter-page Go action when the site requires it before the item grid appears.
