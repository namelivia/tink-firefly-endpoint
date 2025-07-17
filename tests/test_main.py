import os
import json
from unittest.mock import Mock, patch
from datetime import datetime

from app.utils.utils import (
    iterate_transactions,
    check_tink_account_balance,
    check_firefly_account_balance,
)
from app.summary.summary import Summary
from dataclass_map_and_log.mapper import DataclassMapper
from tink_python_api_types.transaction import TransactionsPage
from tink_python_api_types.account import AccountsPage
import humps


class TestApp:
    def _get_tink_stub_contents(self, stub_name, class_name):
        path = os.path.join(os.path.dirname(__file__), "./stubs/tink/")
        with open(path + stub_name) as stub_data:
            data = humps.decamelize(json.load(stub_data))
            return DataclassMapper.map(class_name, data)

    def _get_firefly_stub_contents(self, stub_name):
        path = os.path.join(os.path.dirname(__file__), "./stubs/firefly/")
        with open(path + stub_name) as stub_data:
            return json.load(stub_data)

    @patch("app.utils.fix_transactions.load_config")
    def test_iterating_and_fixing_transactions_for_blue_bank(self, load_config_mock):
        stub_data = self._get_tink_stub_contents(
            "blue_bank/transaction_page.json", TransactionsPage
        )
        load_config_mock.return_value = {
            "account_middleware_mapping": {
                "blue_account_id": "blue",
                "red_account_id": "red",
            }
        }

        account_id = "blue_account_id"
        tink = Mock()
        date_until = datetime.strptime("2020-12-13", "%Y-%m-%d")
        tink.transactions.return_value.get.return_value = stub_data

        fixed_transactions = iterate_transactions(account_id, date_until, tink)
        tink.transactions.return_value.get.assert_called_once_with(pageToken=None)
        assert fixed_transactions == [
            {
                "amount": -130.0,
                "date": "2020-12-15",
                "description": "Tesco",
                "id": "d8f37f7d19c240abb4ef5d5dbebae4ef",
                "provider_transaction_id": "d8f37f7d19c240abb4ef5d5dbebae4ef",
            }
        ]

    @patch("app.utils.fix_transactions.load_config")
    def test_iterating_and_fixing_transactions_for_red_bank(self, load_config_mock):
        stub_data = self._get_tink_stub_contents(
            "red_bank/transaction_page.json", TransactionsPage
        )
        load_config_mock.return_value = {
            "account_middleware_mapping": {
                "blue_account_id": "blue",
                "red_account_id": "red",
            }
        }

        account_id = "red_account_id"
        tink = Mock()
        date_until = datetime.strptime("2020-12-13", "%Y-%m-%d")
        tink.transactions.return_value.get.return_value = stub_data

        fixed_transactions = iterate_transactions(account_id, date_until, tink)
        tink.transactions.return_value.get.assert_called_once_with(pageToken=None)
        assert fixed_transactions == [
            {
                "amount": -130.0,
                "date": "2020-12-15",
                "description": "Tesco",
                "id": "d8f37f7d19c240abb4ef5d5dbebae4ef",
                "provider_transaction_id": "d8f37f7d19c240abb4ef5d5dbebae4ef",
            }
        ]

    def test_check_checking_the_tink_account_balance(self):
        tink = Mock()
        stub_data = self._get_tink_stub_contents("accounts.json", AccountsPage)
        tink.accounts.return_value.get.return_value = stub_data

        account_id = "account_id"
        balance = check_tink_account_balance(account_id, tink)
        assert balance == 19000.0
        tink.accounts.return_value.get.assert_called_once_with()

    def test_checking_the_firefly_account_balance(self):
        firefly = Mock()
        stub_data = self._get_firefly_stub_contents("account.json")
        firefly.get_account_balance.return_value = stub_data

        account_id = "account_id"
        balance = check_firefly_account_balance(account_id)
        assert balance is None  # The function is not yet implemented
