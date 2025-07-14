from tink_http_python.transactions import Transactions
from abc import ABC, abstractmethod


class AccountMiddleware(ABC):
    def __init__(self, account_id):
        self.account_id = account_id

    @abstractmethod
    def fix_transaction(self, transaction) -> dict:
        pass


class SomeAccountMiddleware(AccountMiddleware):
    def _get_provider_transaction_id(self, transaction):
        if transaction.identifiers is not None:
            return transaction.identifiers.provider_transaction_id
        return ""

    def fix_transaction(self, transaction):
        fixed_transaction = {
            "amount": Transactions.calculate_real_amount(transaction.amount.value),
            "date": transaction.dates.value,
            "description": transaction.descriptions.display,
            "id": transaction.id,
            "provider_transaction_id": self._get_provider_transaction_id(transaction),
        }
        return fixed_transaction
