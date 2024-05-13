"""Prints some information based on data retrieved from bank statement
"""

from transactions_list_reader import FioTransactionsListReader
from transactions_list_reader import CsobTransactionsListReader
from transactions_list_reader import CSTransactionsListReader

change_path_to_examples_folder = True

def print_principal_tax_added_interest_rate(transaction_list_reader):
    """Prints principal, deducted tax and added interest rate

    Args:
        transaction_list_reader (TransactionListReader): instance of class TransactionListReader
    """
    print(
        f"{transaction_list_reader.directory} total added interest rate: ",
        transaction_list_reader.get_total_added_interest_rate(),
    )
    print(
        f"{transaction_list_reader.directory} total deducted tax on interest: ",
        transaction_list_reader.get_total_deducted_tax_on_interest(),
    )
    print(
        f"{transaction_list_reader.directory} total principal: ",
        transaction_list_reader.get_total_principal(),
    )


csobReader = CsobTransactionsListReader()
if change_path_to_examples_folder: 
    csobReader.directory = "examples/csob"
all_transactions_lists_csob = csobReader.read_all_transactions_lists()
print(all_transactions_lists_csob)
print_principal_tax_added_interest_rate(csobReader)

fioTransactionsListReader = FioTransactionsListReader()
if change_path_to_examples_folder: 
    fioTransactionsListReader.directory = "examples/fio"
all_transactions_lists_fio = fioTransactionsListReader.read_all_transactions_lists()
print(all_transactions_lists_fio)
print_principal_tax_added_interest_rate(fioTransactionsListReader)

csTransactionsListReader = CSTransactionsListReader()
if change_path_to_examples_folder: 
    csTransactionsListReader.directory = "examples/cs"
all_transactions_lists_cs = csTransactionsListReader.read_all_transactions_lists()
print(all_transactions_lists_cs)
print_principal_tax_added_interest_rate(csTransactionsListReader)

total_added_interest_rate = float()
total_principal = float()
total_deducted_tax_on_iterest = float()
for transactionReader in [
    csobReader,
    fioTransactionsListReader,
    csTransactionsListReader,
]:
    total_added_interest_rate += transactionReader.get_total_added_interest_rate()
    total_principal += transactionReader.get_total_principal()
    total_deducted_tax_on_iterest += (
        transactionReader.get_total_deducted_tax_on_interest()
    )

print(
    f"csob + fio + cs: total added interest rate: {total_added_interest_rate},"
    f"total principal: {total_principal}, "
    f"total deduced tax on interest {total_deducted_tax_on_iterest}"
)
print(
    f"csob + fio + cs (*0.17 - pln): "
    f"total added interest rate: {total_added_interest_rate * 0.17},"
    f"total principal: {total_principal * 0.17}, "
    f"total deduced tax on interest {total_deducted_tax_on_iterest * 0.17}"
)
print(
    f"total added interest rate (tax 0.15): {total_added_interest_rate * 0.85},"
    f"total added interest rate (tax 0.19): {total_added_interest_rate * 0.81},"
    f"diff: {total_added_interest_rate * 0.81 - total_added_interest_rate * 0.85}"
)
print(
    f"total added interest rate (tax 0.15 *0.17pln): {total_added_interest_rate * 0.85 * 0.17},"
    f"total added interest rate (tax 0.19 *0.17pln): {total_added_interest_rate * 0.81 * 0.17},"
    f"diff: {(total_added_interest_rate * 0.81 - total_added_interest_rate * 0.85)*0.17}"
)
