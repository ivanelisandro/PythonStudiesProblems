import random
import sqlite3


def print_spacing(message):
    print()
    print(message)
    print()


def start_menu():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")


def logged_menu():
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")


class Account:
    select_balance_query = "SELECT balance " \
                           "FROM card " \
                           "WHERE id={0};"

    update_balance_query = "UPDATE card " \
                           "SET balance = balance+({1}) " \
                           "WHERE number={0};"

    exist_card_query = "SELECT EXISTS(" \
                       "SELECT 1 FROM card WHERE number='{0}' LIMIT 1" \
                       ");"

    def __init__(self, account_number, card_number, pin, connection, cursor):
        self.account_number = account_number
        self.card_number = card_number
        self.pin = pin
        self.connection = connection
        self.cursor = cursor

    def created_account(self):
        print()
        print("Your card has been created")
        print("Your card number:")
        print(self.card_number)
        print("Your card PIN:")
        print(str(self.pin).zfill(4))
        print()

    def login(self):
        print_spacing("You have successfully logged in!")
        while True:
            logged_menu()
            selection = int(input())
            if selection == 1:
                print_spacing("Balance: " + str(self.get_balance()))
            elif selection == 2:
                self.start_add_income()
            elif selection == 3:
                self.start_do_transfer()
            elif selection == 5:
                print_spacing("You have successfully logged out!")
                break
            elif selection == 0 or selection == 4:
                break
            else:
                print_spacing("Invalid option!")
        return selection

    def get_balance(self):
        self.cursor.execute(Account.select_balance_query.format(self.account_number))
        return self.cursor.fetchone()[0]

    def start_add_income(self):
        print()
        print("Enter income:")
        income = int(input())
        if income > 0:
            self.add_income(income)

    def add_income(self, income):
        self.cursor.execute(Account.update_balance_query.format(self.card_number, income))
        self.connection.commit()
        print("Income was added!")
        print()

    def start_do_transfer(self):
        print()
        print("Transfer")
        print("Enter card number:")
        destination = str(input())
        if self.is_same_card(destination):
            print("You can't transfer money to the same account!")
        elif not Bank.is_valid_luhn_card(destination):
            print("Probably you made a mistake in the card number. Please try again!")
        elif not self.destination_exist(destination):
            print("Such a card does not exist.")
        else:
            print("Enter how much money you want to transfer:")
            amount_to_transfer = int(input())

            if not self.has_enough_money(amount_to_transfer):
                print("Not enough money!")
                print()
                return

            self.do_transfer(destination, amount_to_transfer)
            print("Success!")
        print()

    def do_transfer(self, destination, amount_to_transfer):
        self.cursor.execute(Account.update_balance_query.format(self.card_number, -amount_to_transfer))
        self.connection.commit()
        self.cursor.execute(Account.update_balance_query.format(destination, amount_to_transfer))
        self.connection.commit()

    def has_enough_money(self, amount_to_transfer):
        balance = self.get_balance()
        return balance >= amount_to_transfer

    def is_same_card(self, card):
        return card == self.card_number

    def destination_exist(self, card):
        self.cursor.execute(Account.exist_card_query.format(card))
        destination_exist = self.cursor.fetchone()[0]
        if destination_exist:
            return True
        return False


class Bank:
    create_card_table_query = "CREATE TABLE IF NOT EXISTS card (" \
                              "    id INTEGER," \
                              "    number TEXT," \
                              "    pin TEXT," \
                              "    balance INTEGER DEFAULT 0" \
                              ");"

    insert_card_query = "INSERT INTO card(id, number, pin) " \
                        "VALUES ({0}, {1}, {2});"

    exist_account_query = "SELECT EXISTS(" \
                          "SELECT 1 FROM card WHERE id={0} LIMIT 1" \
                          ");"

    delete_account_query = "DELETE FROM card WHERE id={0}"

    select_client_info_query = "SELECT id, number, pin, balance " \
                               "FROM card " \
                               "WHERE number='{0}' AND pin={1};"

    def __init__(self):
        self.bin = 400000
        self.connection = None
        self.cursor = None

    def start(self):
        self.init_database()
        while True:
            start_menu()
            selection = int(input())
            if selection == 1:
                self.create_account()
            elif selection == 2:
                selection = self.start_login()
            elif selection != 0:
                print_spacing("Invalid option!")

            if selection == 0:
                self.finish_database()
                print_spacing("Bye!")
                break

    def init_database(self):
        self.connection = sqlite3.connect('card.s3db')
        self.cursor = self.connection.cursor()
        self.cursor.execute(Bank.create_card_table_query)
        self.connection.commit()

    def finish_database(self):
        if self.connection:
            self.connection.close()

    def exist_account(self, account_number):
        self.cursor.execute(Bank.exist_account_query.format(account_number))
        client_exist = self.cursor.fetchone()[0]
        if client_exist:
            return True
        return False

    def start_login(self):
        print()
        print("Enter your card number:")
        card = input()
        print("Enter your PIN:")
        pin = input()
        account = self.get_account(card, pin)

        if account:
            result = account.login()
            if result == 4:
                self.close_account(account.account_number)
                print_spacing("The account has been closed!")
            else:
                return result
        else:
            print_spacing("Wrong card number or PIN!")
        return -1

    def create_account(self):
        while True:
            account = random.randint(0, 999999999)
            if not self.exist_account(account):
                break
        card = self.create_card(account)
        pin = str(random.randint(0, 9999)).zfill(4)
        self.cursor.execute(Bank.insert_card_query.format(account, card, pin))
        self.connection.commit()
        account = self.get_account(card, pin)
        account.created_account()

    def create_card(self, account_number):
        card_no_checksum = f"{self.bin}{str(account_number).zfill(9)}"
        checksum = Bank.get_checksum(card_no_checksum)
        return f"{card_no_checksum}{checksum}"

    def get_account(self, card, pin):
        if card and pin:
            self.cursor.execute(Bank.select_client_info_query.format(card, pin))
            client = self.cursor.fetchone()
            if client:
                client_account = Account(client[0], client[1], client[2], self.connection, self.cursor)
                return client_account
        return None

    def close_account(self, account_number):
        self.cursor.execute(Bank.delete_account_query.format(account_number))
        self.connection.commit()

    @staticmethod
    def get_checksum(card_no_checksum):
        digits = list(map(int, card_no_checksum))
        for index, value in enumerate(digits):
            if int(index) % 2 == 0:
                digits[index] = value * 2

        sum_digits = 0
        for digit in digits:
            if digit > 9:
                digit = digit - 9
            sum_digits += digit

        if sum_digits % 10 > 0:
            return 10 - sum_digits % 10
        else:
            return 0

    @staticmethod
    def is_valid_luhn_card(card):
        no_checksum = card[:-1]
        value_to_validate = int(card[-1])
        valid_value = Bank.get_checksum(no_checksum)
        return value_to_validate == valid_value


my_bank = Bank()
my_bank.start()
