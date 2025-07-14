from jinja2 import Template
import csv
from app.summary.summary import Summary
import logging
from app.utils.transaction_processor_utils import (
    add_transaction_to_summary,
    write_transaction_to_csv,
    fix_transaction,
)
from datetime import datetime

logger = logging.getLogger(__name__)


def _get_transaction_date(transaction):
    return datetime.strptime(transaction.dates.value, "%Y-%m-%d")


def _date_before_target(transaction, target_date):
    return _get_transaction_date(transaction) < target_date


def _process_transaction(account_id, writer, transaction):
    # This function will add an entry of the transaction to the csv file and the summary
    fixed_transaction = fix_transaction(transaction)
    write_transaction_to_csv(account_id, writer, fixed_transaction)
    add_transaction_to_summary(fixed_transaction)


def _iterate_transactions(account_id, writer, date_until, tink, page):
    page = None
    stop = False
    while not stop:
        transactions_page = tink.transactions().get(pageToken=page)
        stop = process_transactions_page(
            account_id, writer, date_until, transactions_page
        )
        page = transactions_page.next_page_token


def write_csv_file(account_id, tink, date_until, output_path, current_timestamp):
    file_name = f"{output_path}/output_{current_timestamp}.csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f, delimiter=";")
        _iterate_transactions(account_id, writer, date_until, tink, None)


def process_transactions_page(account_id, writer, target_date, transactions_page):
    # This function will add transactions until either all of them are added or the
    # target date is found.
    for transaction in transactions_page.transactions:
        if _date_before_target(transaction, target_date):
            return True
        _process_transaction(account_id, writer, transaction)
    return False


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
