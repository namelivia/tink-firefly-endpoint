from tink_http_python.transactions import Transactions
from abc import ABC, abstractmethod
from typing import Optional


def get_account_middleware(account_id):
    if account_id == "32":
        return SomeAccountMiddleware()
    elif account_id == "17":
        return AnotherAccountMiddleware()
    else:
        raise ValueError(f"Unknown account ID: {account_id}")


class AccountMiddleware(ABC):
    @abstractmethod
    def fix_transaction(self, transaction) -> Optional[dict]:
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


class AnotherAccountMiddleware(AccountMiddleware):
    def _get_provider_transaction_id(self, transaction):
        if transaction.identifiers is not None:
            return transaction.identifiers.provider_transaction_id
        return ""

    def fix_transaction(self, transaction):
        # Ignore credit card transactions
        if transaction.types.type == "CREDIT_CARD":
            return None
        fixed_transaction = {
            "amount": Transactions.calculate_real_amount(transaction.amount.value),
            "date": transaction.dates.value,
            "description": transaction.descriptions.display,
            "id": transaction.id,
            "provider_transaction_id": self._get_provider_transaction_id(transaction),
        }
        return fixed_transaction
