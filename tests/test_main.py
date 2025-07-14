import os
import json
from unittest.mock import Mock
from datetime import datetime

from app.utils.utils import (
    iterate_transactions,
)
from app.summary.summary import Summary
from dataclass_map_and_log.mapper import DataclassMapper
from tink_python_api_types.transaction import TransactionsPage
import humps

mock_transaction = mock_transaction = type(
    "Transaction",
    (object,),
    {"dates": type("Dates", (object,), {"value": "2023-10-01"}), "identifiers": None},
)()


class TestApp:
    def _get_stub_contents(self, stub_name):
        path = os.path.join(os.path.dirname(__file__), "./stubs/")
        with open(path + stub_name) as stub_data:
            data = humps.decamelize(json.load(stub_data))
            return DataclassMapper.map(TransactionsPage, data)

    def test_iterating_and_fixing_transactions(self):
        # Load the stub data for a transactions page from 'transaction_page.json'
        stub_data = self._get_stub_contents("transaction_page.json")
        account_id = "test_account"
        tink = Mock()
        writer = Mock()
        date_until = datetime.strptime("2020-12-13", "%Y-%m-%d")
        tink.transactions.return_value.get.return_value = stub_data

        # Call the _iterate_transactions function with the mock objects
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
