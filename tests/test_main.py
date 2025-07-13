import os
import json
from unittest.mock import Mock
from datetime import datetime

from app.utils.utils import (
    _get_transaction_date,
    _date_before_target,
    _iterate_transactions,
)
from app.utils.transaction_processor_utils import (
    _get_provider_transaction_id,
    add_transaction_to_summary,
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

    # TRANSACTION PROCESSOR UTILS
    def test_getting_the_provider_transaction_id_from_a_transaction(self):
        # The transaction id is extracted, empty string used as
        # a fallback.
        assert _get_provider_transaction_id(mock_transaction) == ""

    def test_iterating_transactions(self):
        stub_data = self._get_stub_contents("transaction_page.json")
        account_id = "test_account"
        tink = Mock()
        writer = Mock()
        date_until = datetime.strptime("2020-12-13", "%Y-%m-%d")
        tink.transactions.return_value.get.return_value = stub_data
        _iterate_transactions(account_id, writer, date_until, tink, None)
        tink.transactions.return_value.get.assert_called_once_with(pageToken=None)
        summary = Summary().get()
        assert len(summary) == 1
        assert summary[0] == {
            "amount": -130.0,
            "date": "2020-12-15",
            "description": "Tesco",
        }
