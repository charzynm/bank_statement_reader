"""Tool for reading positive interest accounting notes from bank statements
"""
import csv
import os
import itertools
from abc import abstractmethod
import datetime

class Transaction:
    """Represents bank transaction
    """
    def __init__(self, date, positive_interest_accounting_note):
        self.date = date
        self.positive_interest_accounting_note = positive_interest_accounting_note

class PositiveInterestAccountingNote:
    """Represents "Positive Interest Accounting Note"
    """
    def __init__(self, transaction_amount = 0.0, principal = 0.0, federal_withholding = 0.0):
        self.transaction_amount = transaction_amount
        self.principal = principal
        self.federal_withholding = federal_withholding

    def __str__(self):
        return f"Transaction Amount: {self.transaction_amount}, " \
            f"Principal: {self.principal}, Federal Withholding: {self.federal_withholding}"

    @classmethod
    def build_from_note_str(cls, note):
        """Build a new object from a string representation

        Args:
            note (str): String representation of an object 
            ('Transaction Amount: 1076,46, Principal: 914,99, Federal Withholding: 161,47')

        Returns:
            PositiveInterestAccountingNote: instance of class PositiveInterestAccountingNote
        """
        value_pairs = note.split(", ")
        note_info = {}
        for value_pair in value_pairs:
            key, value = value_pair.split(": ")
            note_info[key] = float(value.replace(",", "."))
        return cls(
            note_info["Transaction Amount"], note_info["Principal"],
            note_info["Federal Withholding"])

class TransactionsListReader:
    """Represents generic reader of transactions lists
    """
    def __init__(self):
        self.no_of_rows_to_skip = 0
        self.directory = ""
        self.all_transactions_lists = []
        self.positive_interest_accounting_transactions = []
        self.delimiter = ";"
        self.encoding = "UTF-8"

    def read_transactions_list(self, path):
        """Reads list of transactions from a file

        Args:
            path (str): file path

        Returns:
            list: list of transactions
        """
        with open(path, "r", encoding=self.encoding) as csvfile:
            #skipping first two lines
            csvfile = itertools.islice(csvfile, self.no_of_rows_to_skip, None)
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            return list(reader)

    def read_all_transactions_lists(self):
        """Reads list of transactions from all files in a directory

        Args:
            directory (str): directory containing files with transactions

        Returns:
            list: list of transactions
        """
        result_list = []
        for dirpath, _, filenames in os.walk(self.directory):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                result_list += self.read_transactions_list(path)
        self.all_transactions_lists = result_list
        return self.all_transactions_lists

    def get_list_of_transactions(self):
        """Reads all transactions and returns an empty list.
        Child class should handle processing the list and return
        a list of objects of class Transaction

        Returns:
            List: empty list
        """
        self.read_all_transactions_lists()
        return []

    def get_positive_interest_accounting_transactions(self):
        """Gets from the list of all transactions only those 
        related to interest rate and tax
        """
        self.positive_interest_accounting_transactions = (
            [transaction for transaction in self.read_all_transactions_lists()
                if self.is_transaction_type_positive_interest_accounting(transaction)]
        )
        return self.positive_interest_accounting_transactions

    def get_total_added_interest_rate(self):
        """Sums up added interest rate for all transactions

        Returns:
            float: total added interest rate
        """
        return sum(transaction.positive_interest_accounting_note.transaction_amount
                   for transaction in self.get_list_of_transactions())

    def get_total_deducted_tax_on_interest(self):
        """Sums up deducted tax on interest for all transactions

        Returns:
            float: total deduced tax on interest
        """
        return sum(transaction.positive_interest_accounting_note.federal_withholding
                   for transaction in self.get_list_of_transactions())

    def get_total_principal(self):
        """Sums up principal for all transactions

        Returns:
            float: total principal
        """
        return sum(transaction.positive_interest_accounting_note.principal
                   for transaction in self.get_list_of_transactions())

    @abstractmethod
    def is_transaction_type_positive_interest_accounting(self, transaction_str):
        """Checks if transaction is related to positive interest accounting

        Args:
            transaction_str (str): transaction string
        """

class CsobTransactionsListReader(TransactionsListReader):
    """Represents reader of transactions lists from CSOB
    """
    def __init__(self):
        super().__init__()
        self.no_of_rows_to_skip = 2
        self.directory = "csob"
        self.positive_interest_accounting_transactions = (
            self.get_positive_interest_accounting_transactions()
        )

    def get_list_of_transactions(self):
        super().get_list_of_transactions()
        transactions = []
        for trans_str in self.get_positive_interest_accounting_transactions():
            date = datetime.datetime.strptime(trans_str["due date"], "%d.%m.%Y").date()
            positive_interest_accounting_note = (
                self.__get_positive_interest_accounting_transaction(trans_str["note"])
            )
            transactions.append(Transaction(date, positive_interest_accounting_note))
        return transactions

    def is_transaction_type_positive_interest_accounting(self, transaction_str):
        super().is_transaction_type_positive_interest_accounting(transaction_str)
        return transaction_str["transaction type"] == "Positive interest accounting"

    def __get_positive_interest_accounting_transaction(self, note_str):
        return PositiveInterestAccountingNote.build_from_note_str(note_str)

class FioTransactionsListReader(TransactionsListReader):
    """Represents reader of transactions lists from FIO
    """
    def __init__(self):
        super().__init__()
        self.no_of_rows_to_skip = 9
        self.directory = "fio"

    def get_list_of_transactions(self):
        super().get_list_of_transactions()
        trans_with_id = {}
        for trans_str in self.get_positive_interest_accounting_transactions():
            id_of_payment_order = trans_str["ID of payment order"]
            date = datetime.datetime.strptime(trans_str["Date"], "%m/%d/%Y").date()
            amount = float(trans_str["Volume"])
            trans_with_id[id_of_payment_order] = (
                trans_with_id.get(id_of_payment_order,
                                  Transaction(date, PositiveInterestAccountingNote()))
            )
            positive_interest_accounting_note = (
                trans_with_id[id_of_payment_order].positive_interest_accounting_note
            )
            if trans_str["Type"] == "Added interest rate":
                positive_interest_accounting_note.transaction_amount = amount
            elif trans_str["Type"] == "Deducted tax on interest":
                positive_interest_accounting_note.federal_withholding = amount * -1
            if (positive_interest_accounting_note.transaction_amount > 0 and
                positive_interest_accounting_note.federal_withholding > 0):
                positive_interest_accounting_note.principal = (
                    positive_interest_accounting_note.transaction_amount -
                    positive_interest_accounting_note.federal_withholding
                )
        return list(trans_with_id.values())

    def is_transaction_type_positive_interest_accounting(self, transaction_str):
        super().is_transaction_type_positive_interest_accounting(transaction_str)
        transaction_type = transaction_str["Type"]
        return transaction_type in ("Added interest rate", "Deducted tax on interest")

class CSTransactionsListReader(TransactionsListReader):
    """Represents reader of transactions lists from CS
    """
    def __init__(self):
        super().__init__()
        self.directory = "cs"
        self.delimiter = ","
        self.encoding = "UTF-16"

    def get_list_of_transactions(self):
        super().get_list_of_transactions()
        transactions_tmp = []
        trnctns = self.get_positive_interest_accounting_transactions()
        for i in range(len(trnctns)):
            if i % 2 == 0:
                transactions_tmp.append([trnctns[i], trnctns[i + 1]])
        transactions = []
        for trans_arr in transactions_tmp:
            date = datetime.datetime.strptime(trans_arr[0]["Processing Date"], "%d.%m.%Y").date()
            transaction_amount = float(trans_arr[0]["Amount"])
            federal_withholding = float(trans_arr[1]["Amount"]) * -1
            principal = transaction_amount - federal_withholding
            transactions.append(
                Transaction(
                    date,
                    PositiveInterestAccountingNote(
                        transaction_amount, principal, federal_withholding)
                ))
        return transactions

    def is_transaction_type_positive_interest_accounting(self, transaction_str):
        super().is_transaction_type_positive_interest_accounting(transaction_str)
        partner_account_number = transaction_str["Partner Account Number"]
        bank_code = transaction_str["Bank code"]
        transaction_amount = float(transaction_str["Amount"].replace(",", ""))
        return partner_account_number == "" and bank_code == "0" and transaction_amount != 0
