from tink_http_python.transactions import Transactions
from abc import ABC, abstractmethod
from typing import Optional
import yaml


class AccountMiddleware(ABC):
    @abstractmethod
    def fix_transaction(self, transaction) -> Optional[dict]:
        pass


class BlueAccountMiddleware(AccountMiddleware):
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


class RedAccountMiddleware(AccountMiddleware):
    # The Red Bank includes separate credit card transactions,
    # we can ignore them as they will also be duplicated as regular transactions.
    def _get_provider_transaction_id(self, transaction):
        if transaction.identifiers is not None:
            return transaction.identifiers.provider_transaction_id
        return ""

    def fix_transaction(self, transaction):
        if transaction.types.type == "CREDIT_CARD":
            return None  # Ignore credit card transactions
        fixed_transaction = {
            "amount": Transactions.calculate_real_amount(transaction.amount.value),
            "date": transaction.dates.value,
            "description": transaction.descriptions.display,
            "id": transaction.id,
            "provider_transaction_id": self._get_provider_transaction_id(transaction),
        }
        return fixed_transaction


MIDDLEWARE_KEYWORD_MAP = {
    "blue": BlueAccountMiddleware,
    "red": RedAccountMiddleware,
}


def load_config():
    """Loads the configuration from a YAML file."""
    config_path = "config.yaml"
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")


def get_account_middleware(account_id):
    config = load_config()
    middleware_mapping = config.get("account_middleware_mapping", {})
    keyword = middleware_mapping.get(account_id)

    if keyword:
        middleware_class = MIDDLEWARE_KEYWORD_MAP.get(keyword)
        if middleware_class:
            return middleware_class()
        else:
            raise ValueError(
                f"Unknown middleware keyword '{keyword}' found for account ID {account_id}. "
                f"Please check MIDDLEWARE_KEYWORD_MAP."
            )
    else:
        raise ValueError(f"Unknown account ID: {account_id}")
