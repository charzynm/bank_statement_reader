from transactions_list_reader import CSTransactionsListReader

def test_ddd():
    csTransactionsListReader = CSTransactionsListReader()
    csTransactionsListReader.directory = "examples/cs"
    assert csTransactionsListReader.get_total_principal() == 900.00
