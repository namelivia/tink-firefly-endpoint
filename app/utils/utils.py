from jinja2 import Template
import csv
from app.summary.summary import Summary
import logging
from app.utils.csv_utils import (
    write_transaction_to_csv,
)
from app.utils.summary_utils import (
    add_transaction_to_summary,
)
from app.utils.fix_transactions import fix_transaction
from datetime import datetime

logger = logging.getLogger(__name__)


def _get_transaction_date(transaction):
    return datetime.strptime(transaction.dates.value, "%Y-%m-%d")


def _date_before_target(transaction, target_date):
    return _get_transaction_date(transaction) < target_date


def _save_transaction(account_id, writer, transaction):
    # This function will add an entry of the transaction to the csv file and the summary
    write_transaction_to_csv(account_id, writer, transaction)
    add_transaction_to_summary(transaction)


def iterate_transactions(account_id, date_until, tink):
    page = None
    stop = False
    fixed_transactions = []
    while not stop:
        transactions_page = tink.transactions().get(pageToken=page)
        stop, fixed_transactions = process_transactions_page(
            account_id, date_until, fixed_transactions, transactions_page
        )
        page = transactions_page.next_page_token
    return fixed_transactions


def save_transactions(account_id, fixed_transactions, output_path, current_timestamp):
    file_name = f"{output_path}/output_{current_timestamp}.csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f, delimiter=";")
        [
            _save_transaction(account_id, writer, transaction)
            for transaction in fixed_transactions
        ]


def process_transactions_page(
    account_id, target_date, fixed_transactions, transactions_page
):
    # This function will add transactions until either all of them are added or the
    # target date is found.
    for transaction in transactions_page.transactions:
        if _date_before_target(transaction, target_date):
            return True, fixed_transactions
        fixed_transactions.append(fix_transaction(transaction))
    return False, fixed_transactions


def write_configuration_file(account_id, output_path, timestamp):
    configuration_file_name = f"{output_path}/output_{timestamp}.json"
    configuration_template_file_name = "templates/importer_configuration.json"
    with open(configuration_template_file_name, "r") as template_file:
        template_content = template_file.read()
    template = Template(template_content)
    rendered_configuration = template.render(
        {
            "default_account_id": account_id,
        }
    )
    with open(configuration_file_name, "w") as configuration_file:
        configuration_file.write(rendered_configuration)
