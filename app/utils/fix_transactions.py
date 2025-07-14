from tink_http_python.transactions import Transactions


def _get_provider_transaction_id(transaction):
    if transaction.identifiers is not None:
        return transaction.identifiers.provider_transaction_id
    return ""


def _get_transaction_date(transaction):
    return transaction.dates.value


def fix_transaction(transaction):
    # Some fixes need to be applied to the transaction
    # before it can be written.
    fixed_transaction = {
        "amount": Transactions.calculate_real_amount(transaction.amount.value),
        "date": _get_transaction_date(transaction),
        "description": transaction.descriptions.display,
        "id": transaction.id,
        "provider_transaction_id": _get_provider_transaction_id(transaction),
    }
    return fixed_transaction
