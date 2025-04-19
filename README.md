# SavingYNAB
## Features
Customizably uses YNAB data to calculate savings rate, total earnings, and total spending for any period with optional drill down detail.

![](screenshots/savings_dtl.png)

This project is entirely open source and private. Currently runs exclusively in the terminal.

## Setup
1) `pip install ynab`
2) Clone this repository
3) Generate a `Personal Access Token`
   1) [Sign in to the YNAB web app](https://app.ynab.com/settings) and go to the "Account Settings" page and then to the "Developer Settings" page.
   2) Under the "Personal Access Tokens" section, click "New Token", enter your password and click "Generate" to get an access token.
   3) Copy the token from the top of the screen. It is irrecoverable after refresh.
4) Provide your access token in `Run.py`
5) Adjust the following customization functions. They each take a [YNAB `TransactionDetail` object](https://github.com/ynab/ynab-sdk-python/blob/main/docs/TransactionDetail.md) and return `bool`. 
    - They determine what qualifies as a transaction, earnings, and spending.
   - Using the example code and linked documentation, adjust them to what you find appropriate.
    ```
    by_transaction_criteria
    by_earning_criteria
    by_spending_criteria
    ```
6) Execute `python3 /SavingYNAB/run.py`
   * Another option for MacOS: Make `SavingYNAB.command` executable (`chmod +x SavingYNAB.command`) and simply double click.