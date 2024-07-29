import datetime
import mysql.connector
import pandas as pd

db = mysql.connector.connect(
    host="localhost",
    user="___",
    password="___",
    database="AccountingDB"
)
cursor = db.cursor()

def post_journal_entry(date, account, description, debit, credit):
    query = "INSERT INTO Journal (date, account, description, debit, credit) VALUES (%s, %s, %s, %s, %s)"
    values = (date, account, description, debit, credit)
    cursor.execute(query, values)
    db.commit()

def convert_to_ledger():
    cursor.execute("DELETE FROM Ledger")
    db.commit()
    
    cursor.execute("SELECT account, SUM(debit - credit) as balance FROM Journal GROUP BY account")
    ledger_entries = cursor.fetchall()
    
    for entry in ledger_entries:
        account, balance = entry
        query = "INSERT INTO Ledger (account, balance) VALUES (%s, %s)"
        values = (account, balance)
        cursor.execute(query, values)
        db.commit()

def generate_balance_sheet():
    cursor.execute("DELETE FROM BalanceSheet")
    db.commit()
    
    cursor.execute("SELECT account, balance FROM Ledger")
    ledger_entries = cursor.fetchall()
    
    for entry in ledger_entries:
        account, balance = entry
        category = "Assets" if balance > 0 else "Liabilities"
        if balance == 0:
            category = "Equity"
        query = "INSERT INTO BalanceSheet (account, category, amount) VALUES (%s, %s, %s)"
        values = (account, category, abs(balance))
        cursor.execute(query, values)
        db.commit()

def view_journal():
    cursor.execute("SELECT * FROM Journal")
    entries = cursor.fetchall()
    if entries:
        print("Journal Entries:")
        for entry in entries:
            print(entry)
    else:
        print("No journal entries found.")

def view_ledger():
    cursor.execute("SELECT * FROM Ledger")
    entries = cursor.fetchall()
    if entries:
        print("Ledger Entries:")
        for entry in entries:
            print(entry)
    else:
        print("No ledger entries found.")

def view_balance_sheet():
    cursor.execute("SELECT * FROM BalanceSheet")
    entries = cursor.fetchall()
    if entries:
        print("Balance Sheet Entries:")
        for entry in entries:
            print(entry)
    else:
        print("No balance sheet entries found.")

def export_to_excel():
    cursor.execute("SELECT * FROM Journal")
    journal_entries = cursor.fetchall()
    cursor.execute("SELECT * FROM Ledger")
    ledger_entries = cursor.fetchall()
    cursor.execute("SELECT * FROM BalanceSheet")
    balance_sheet_entries = cursor.fetchall()

    journal_df = pd.DataFrame(journal_entries, columns=['ID', 'Date', 'Account', 'Description', 'Debit', 'Credit'])
    ledger_df = pd.DataFrame(ledger_entries, columns=['ID', 'Account', 'Balance'])
    balance_sheet_df = pd.DataFrame(balance_sheet_entries, columns=['ID', 'Account', 'Category', 'Amount'])

    with pd.ExcelWriter('accounting_data.xlsx') as writer:
        journal_df.to_excel(writer, sheet_name='Journal', index=False)
        ledger_df.to_excel(writer, sheet_name='Ledger', index=False)
        balance_sheet_df.to_excel(writer, sheet_name='Balance Sheet', index=False)

def main():
    while True:
        print("\nChoose an option:")
        print("1. Enter a journal entry")
        print("2. View journal entries")
        print("3. Convert journal entries to ledger")
        print("4. Generate balance sheet from ledger")
        print("5. View ledger")
        print("6. View balance sheet")
        print("7. Export data to Excel")
        print("8. Exit")
        
        choice = input("Enter your choice (1-8): ")
        
        print()
        
        if choice == '1':
            date_input = input("Date (YYYY-MM-DD): ")
            try:
                date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format. Please try again.")
                continue

            account = input("Account: ").upper()
            description = input("Description: ")

            try:
                debit = float(input("Debit: "))
            except ValueError:
                print("Invalid amount for debit. Please enter a number.")
                continue

            try:
                credit = float(input("Credit: "))
            except ValueError:
                print("Invalid amount for credit. Please enter a number.")
                continue

            post_journal_entry(date, account, description, debit, credit)
            print("Journal entry posted successfully.")
        
        elif choice == '2':
            view_journal()
        
        elif choice == '3':
            convert_to_ledger()
            print("Journal entries converted to ledger.")
        
        elif choice == '4':
            generate_balance_sheet()
            print("Ledger converted to balance sheet.")
        
        elif choice == '5':
            view_ledger()
        
        elif choice == '6':
            view_balance_sheet()
        
        elif choice == '7':
            export_to_excel()
            print("Data exported to accounting_data.xlsx.")
        
        elif choice == '8':
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")

if __name__ == "__main__":
    main()
