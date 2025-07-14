from jinja2 import Template
import csv
from app.summary.summary import Summary
import logging
from app.summary.summary import Summary
from app.utils.fix_transactions import SomeAccountMiddleware
from datetime import datetime

logger = logging.getLogger(__name__)


def _date_before_target(transaction_date, target_date):
    return datetime.strptime(transaction_date, "%Y-%m-%d") < target_date


def iterate_transactions(account_id, date_until, tink):
    page = None
    stop = False
    fixed_transactions = []
    while not stop:
        transactions_page = tink.transactions().get(pageToken=page)
        stop, fixed_transactions = _process_transactions_page(
            account_id, date_until, fixed_transactions, transactions_page
        )
        page = transactions_page.next_page_token
    return fixed_transactions


def _process_transactions_page(
    account_id, target_date, fixed_transactions, transactions_page
):
    middleware = SomeAccountMiddleware(account_id)
    for transaction in transactions_page.transactions:
        fixed_transaction = middleware.fix_transaction(transaction)
        if _date_before_target(fixed_transaction["date"], target_date):
            return True, fixed_transactions
        else:
            fixed_transactions.append(fixed_transaction)
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


def save_transactions(account_id, fixed_transactions, output_path, current_timestamp):
    file_name = f"{output_path}/output_{current_timestamp}.csv"
    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        for transaction in fixed_transactions:
            writer.writerow(
                (
                    account_id,
                    transaction["date"],
                    transaction["description"],
                    transaction["provider_transaction_id"],
                    transaction["amount"],
                    transaction["id"],
                )
            )
            Summary().add(transaction)
