import os
import sys
from datetime import datetime, date
import calendar

# YNAB API
import ynab # docs (https://github.com/ynab/ynab-sdk-python?tab=readme-ov-file)
from ynab.models.transaction_cleared_status import TransactionClearedStatus
from ynab.models.transaction_detail import TransactionDetail

"""
HELPER FUNCTIONS
"""
def default_filter(func, end_date):
    def wrapper(*args, **kwargs):
        t = args[0]
        return func(*args, **kwargs) and \
            (t.approved or t.cleared != TransactionClearedStatus.UNCLEARED) \
            and t.var_date <= datetime.strptime(end_date, "%Y-%m-%d").date() \
            and t.deleted == False \
            and t.transfer_account_id is None
    return wrapper   

def _write_txt(string, file_name="out"):
    with open(f"{file_name}.txt", "w") as file:
        file.write(string)

def print_table(transactions):
    print(f"{'account_name':<20}  {'payee_name':<26}  {'flag':<6}  {'date':^10}  {'amount':>7}  {'memo':<27}".upper())
    print(*transactions, sep="\n")
    print()

def get_total(transactions):
    return sum(map(lambda t: t.amount or 0, transactions))

"""
YNAB FUNCTIONS
"""
# monkey patch str function
def _transactionDetailToStr(self):
    color = "\033[31m" if self.amount < 0 else "\033[32m"
    return f"{self.account_name[:20]:<20}  {self.payee_name[:26]:<26}  {self.flag_color.name if self.flag_color else '':<6}  {str(self.var_date):<10}  {color}{self.amount / 1000:>7.2f}\033[0m  {(self.memo or '')[:27]:<27}"
TransactionDetail.__str__ = _transactionDetailToStr

def get_transactions(start_date, end_date=date.today().isoformat()):
    with ynab.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = ynab.TransactionsApi(api_client)

        # List transactions
        api_response = api_instance.get_transactions('last-used', since_date=start_date)
        
        from run import by_transaction_criteria
        transactions = list(filter(
            default_filter(by_transaction_criteria, end_date),
            api_response.data.transactions
        ))

        # Empty Case Handling
        if len(transactions) > 0:
            print(f"TransactionsApi->get_transactions: success\n\t(from: {start_date}, to: {end_date})")
            return transactions
        raise Exception(f"No valid transactions found during interval\n\t(from: {start_date}, to: {end_date})")
"""
MENU
"""
def saving_page():
    is_valid = False
    while not is_valid:
        print("Will you specify an end date?")
        print("\tY: Yes")
        print("\tN: No, use today's date")

        end_date_selection = input("Enter: ").strip().lower()
        is_valid = end_date_selection in ['y', 'n']
        
        print()

    print("How would you like to specify a date range?")
    print("\tT: Type manually")
    print("\tM: Month")
    if end_date_selection == 'n':
        print("\tD: Duration")
    print("\tQ: Quit")

    selection = input("Enter: ").strip().lower()
    print()
    match selection:
        case 't':
            start_date = input("Enter YYYY-MM-DD Start Date: ").strip()
            if end_date_selection == 'y':
                end_date = input("Enter YYYY-MM-DD End Date: ").strip()
        case 'm':
            # today
            today = date.today()
            year = today.year
            curr_month = today.month

            # start date
            start_month = input("Enter Start Month Number: ").strip().zfill(2)
            start_year = year - 1 if int(start_month) > curr_month else year
            start_date = f"{start_year}-{start_month}-01"

            # end date
            if end_date_selection == 'y':
                end_month = int(input("Enter End Month Number: ").strip())
                end_year = year - 1 if end_month > curr_month else year
                last_day = calendar.monthrange(year, end_month)[1]

                end_date = f"{end_year}-{end_month:02}-{last_day:02}"
        case 'd':
            if end_date_selection == 'n':
                duration = int(input("Enter how many months would you like to view: ").strip())
                today = date.today()
                year = today.year + ((today.month - duration) // 12)
                month = (today.month - duration) % 12 + 1
                
                start_date = f"{year}-{month:02}-01"
            else:
                return saving_page
        case 'q':
            return root_page
        case _:
            return saving_page
        
    logo()
    try:
        if 'end_date' in locals():
            transactions = get_transactions(start_date, end_date)
        else:
            transactions = get_transactions(start_date)
    except Exception as e:
        print(f"Exception when calling TransactionsApi->get_transactions: {e}")
        return root_page

    is_valid = False
    a_chk_box = " "
    e_chk_box = " "
    s_chk_box = " "
    while not is_valid:
        print("\nWould you like to print transactions?")
        print(f"\tA: Print all [{a_chk_box}]")
        print(f"\tE: Print earnings [{e_chk_box}]")
        print(f"\tS: Print spending [{s_chk_box}]")
        print("\tC: Continue")

        print_selection = input("Enter: ").strip().lower()
        match print_selection:
            case 'a':
                a_chk_box = ' ' if a_chk_box.strip() else 'X'
            case 'e':
                e_chk_box = ' ' if e_chk_box.strip() else 'X'
            case 's':
                s_chk_box = ' ' if s_chk_box.strip() else 'X'
            case 'c':
                is_valid = True

    from run import by_earning_criteria, by_spending_criteria
    inflow = list(filter(by_earning_criteria, transactions))
    outflow = list(filter(by_spending_criteria, transactions))
 
    logo()

    if a_chk_box == 'X':
        print_table(transactions)
    if e_chk_box == 'X':
        print_table(inflow)
    if s_chk_box == 'X':
        print_table(outflow)

    earning = get_total(inflow)
    spending = abs(get_total(outflow))

    print(f"Savings Rate: {(1 - (spending/earning)) * 100:>.3f}%".center(106))
    print(f"Earnings: ${earning / 1000:>9,.2f}".center(106))
    print(f"Spending: ${spending / 1000:>9,.2f}".center(106))

    return root_page

def payee_page():
    logo()
    print("wip") #use PayeesApi
    return root_page

def root_page():
    print("What would you like to do?")
    # print("\tP: Manage payees")
    print("\tS: View savings data")
    print("\tQ: Quit")

    selection = input("Enter: ").strip().lower()
    match selection:
        # case 'p':
        #     return payee_page
        case 's':
            return saving_page
        case 'q':
            return sys.exit
        case _:
            return root_page

def logo():
    os.system('clear||cls') # clear terminal
    print("""
\t  ______                  _                 ____  ____  ____  _____       _       ______    
\t.' ____ \                (_)               |_  _||_  _||_   \|_   _|     / \     |_   _ \   
\t| (___ \_| ,--.  _   __  __   _ .--.   .--./)\ \  / /    |   \ | |      / _ \      | |_) |  
\t _.____`. `'_\ :[ \ [  ][  | [ `.-. | / /'`\; \ \/ /     | |\ \| |     / ___ \     |  __'.  
\t| \____) |// | |,\ \/ /  | |  | | | | \ \._// _|  |_    _| |_\   |_  _/ /   \ \_  _| |__) | 
\t \______.'\'-;__/ \__/  [___][___||__].',__` |______|  |_____|\____||____| |____||_______/  
\t                                     ( ( __))                                               """)
    print("-=" * 53 + "-")

def bootSavingYNAB(token):
        global configuration 
        configuration = ynab.Configuration(access_token = token)

        logo()

        print("\nWelcome to SavingYNAB")
        print("=====================")
        print("SETUP: Supply your YNAB access token to the boot function in the `run.py` file.")
        print("       Then expand your terminal window to fit the entire logo.")
        print("\nPERSONALIZATION:")
        print("- The following functions return a boolean.")
        print("- They determine what qualifies as a transaction, earnings, and spending.")
        print("- Using the example code and linked documentation, adjust them to what you find appropriate.")
        print("\t`by_transaction_criteria`")
        print("\t`by_earning_criteria`")
        print("\t`by_spending_criteria`")
        
        menu = root_page
        while True:
            print()
            try:
                menu = menu()
            except Exception as e:
                print(f"An error was caught ({e}), please begin again.")
