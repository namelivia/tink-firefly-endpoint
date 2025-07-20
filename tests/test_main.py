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

    @patch("app.utils.utils.requests")
    def test_check_checking_the_tink_account_balance(self, mock_requests):
        stub_data = self._get_firefly_stub_contents("account.json")
        mock_requests.get.return_value.json.return_value = stub_data
        mock_requests.get.return_value.status_code = 200
        account_id = "blue_account_id"
        balance = check_firefly_account_balance(account_id)
        mock_requests.get.assert_called_once_with(
            "https://firefly-iii.example.com/api/v1/accounts/blue_account_id",
            headers={
                "Authorization": "Bearer YOUR_API_TOKEN",
                "Accept": "application/json",
            },
        )
        assert balance == 123.45
