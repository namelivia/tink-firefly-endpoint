from app.summary.summary import Summary
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
    fixed_transaction = transaction
    return fixed_transaction


def add_transaction_to_summary(transaction):
    Summary().add(
        {
            "date": _get_transaction_date(transaction),
            "description": transaction.descriptions.display,
            "amount": Transactions.calculate_real_amount(transaction.amount.value),
        }
    )


def write_transaction_to_csv(account_id, writer, transaction):
    transaction_date = _get_transaction_date(transaction)
    writer.writerow(
        (
            account_id,
            transaction_date,
            transaction.descriptions.display,
            _get_provider_transaction_id(transaction),
            Transactions.calculate_real_amount(transaction.amount.value),
            transaction.id,
        )
    )
