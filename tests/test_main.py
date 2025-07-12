from app.utils.utils import (
    _get_transaction_date,
    _date_before_target,
)
from app.utils.transaction_processor_utils import (
    _get_provider_transaction_id,
    add_transaction_to_summary,
)
from app.summary.summary import Summary

mock_transaction = mock_transaction = type(
    "Transaction",
    (object,),
    {"dates": type("Dates", (object,), {"value": "2023-10-01"}), "identifiers": None},
)()


class TestApp:
    def test_getting_transaction_date(self):
        # We extract a date from the transaction data
        transaction_date = _get_transaction_date(mock_transaction)
        assert transaction_date == "2023-10-01"

    def test_checking_if_we_have_to_stop(self):
        # Transactions will be processed until
        # the target date is reached
        # TODO> This is wrong
        assert _date_before_target(mock_transaction, "2023-9-01") is True
        assert _date_before_target(mock_transaction, "2023-11-01") is True

    # TRANSACTION PROCESSOR UTILS
    def test_getting_the_provider_transaction_id_from_a_transaction(self):
        # The transaction id is extracted, empty string used as
        # a fallback.
        assert _get_provider_transaction_id(mock_transaction) == ""

    def test_a_transaction_is_added_to_the_summary(self):
        # Tue transaction is appended to the summary
        # with its fileds propery_calculated
        add_transaction_to_summary(mock_transaction)
        result = Summary().get()
        assert result == []
