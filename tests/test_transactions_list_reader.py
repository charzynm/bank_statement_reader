from transactions_list_reader import FioTransactionsListReader
from transactions_list_reader import CsobTransactionsListReader
from transactions_list_reader import CSTransactionsListReader

def test_get_total_principal_cs():
    csTransactionsListReader = CSTransactionsListReader()
    csTransactionsListReader.directory = "examples/cs"
    assert csTransactionsListReader.get_total_principal() == 900.00

def test_get_total_principal_csob():
    csobReader = CsobTransactionsListReader()
    csobReader.directory = "examples/csob"
    assert csobReader.get_total_principal() == 2700.00

def test_get_total_principal_fio():
    fioTransactionsListReader = FioTransactionsListReader()
    fioTransactionsListReader.directory = "examples/fio"
    assert fioTransactionsListReader.get_total_principal() == 800.00
