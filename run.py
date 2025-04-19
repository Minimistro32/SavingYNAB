
from saving_ynab import bootSavingYNAB
from ynab.models.transaction_flag_color import TransactionFlagColor

"""
MAIN
"""
if __name__ == "__main__":
    # read key from file, otherwise use token
    try:
        with open('/Users/tysonfreeze/Desktop/SavingYNAB/key.txt') as f:
            token = f.read()
    except FileNotFoundError:
        token = "INSERT_API_KEY_HERE" # <-------------

    bootSavingYNAB(token)

"""
CUSTOMIZATION FUNCTIONS
https://github.com/ynab/ynab-sdk-python/blob/main/docs/TransactionDetail.md
"""
# ADJUST THE CRITERIA FOR WHAT QUALIFIES AS A TRANSACTION HERE
def by_transaction_criteria(t):
    return t.account_name not in ['401(k) - CONTINENTAL BATTERY', 'Roth IRA']
        
# ADJUST THE CRITERIA FOR EARNING HERE
def by_earning_criteria(t):
    return t.amount > 0 and (
            t.flag_color == TransactionFlagColor.GREEN \
            or "Continental" in (t.payee_name or '') \
            or "Kroger" in (t.payee_name or '') \
        )

# ADJUST THE CRITERIA FOR SPENDING HERE
def by_spending_criteria(t):
    return t.amount < 0 and t.flag_color is None