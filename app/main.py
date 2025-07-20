import os
import sys
import time
from datetime import datetime
from app.storage.storage import TokenStorage
from app.summary.summary import Summary
from app.utils.utils import (
    iterate_transactions,
    save_transactions,
    write_configuration_file,
    check_tink_account_balance,
    check_firefly_account_balances,
)
from tink_http_python.tink import Tink
from tink_http_python.exceptions import NoAuthorizationCodeException

from fastapi import FastAPI, Query, Cookie, HTTPException
from fastapi.responses import RedirectResponse
import requests
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
from http.client import HTTPConnection

HTTPConnection.debuglevel = 1
requests_logger = logging.getLogger("requests.packages.urllib3")
requests_logger.setLevel(logging.DEBUG)
requests_logger.propagate = True

logger = logging.getLogger(__name__)


@app.get("/")
def read_root(
    code: str = Query(
        ..., title="Authorization Code", description="The authorization code"
    ),
    credentials_id: str = Query(
        ..., title="Credentials ID", description="The credentials ID"
    ),
    date_until: str = Cookie(default=None),
    account_id: str = Cookie(default=None),
):
    # Validate input is correct
    if date_until is None:
        raise HTTPException(status_code=400, detail="date_until cookie not found")
    try:
        formatted_date_until = datetime.strptime(date_until, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format is not valid")

    if account_id is None:
        raise HTTPException(status_code=400, detail="account_id cookie not found")

    # Store the authorization code
    storage = TokenStorage()
    storage.store_new_authorization_code(code)

    # Initialize the API
    tink = Tink(
        client_id=os.environ.get("TINK_CLIENT_ID"),
        client_secret=os.environ.get("TINK_CLIENT_SECRET"),
        redirect_uri=os.environ.get("TINK_CALLBACK_URI"),
        storage=storage,
    )

    # Get the configuration
    output_path = os.environ.get("CSV_PATH")
    current_timestamp = int(time.time())

    # Iterate the transactions and write them to a CSV file
    fixed_transactions = iterate_transactions(account_id, formatted_date_until, tink)
    save_transactions(account_id, fixed_transactions, output_path, current_timestamp)
    write_configuration_file(account_id, output_path, current_timestamp)
    return {"Status": "OK", "Summary": Summary().get()}


@app.get("/check_balance")
def check_balances(
    code: str = Query(
        ..., title="Authorization Code", description="The authorization code"
    ),
    account_id: str = Cookie(default=None),
):
    # Validate input is correct
    if account_id is None:
        raise HTTPException(status_code=400, detail="account_id cookie not found")

    # Store the authorization code
    storage = TokenStorage()
    storage.store_new_authorization_code(code)

    # Initialize the API
    tink = Tink(
        client_id=os.environ.get("TINK_CLIENT_ID"),
        client_secret=os.environ.get("TINK_CLIENT_SECRET"),
        redirect_uri=os.environ.get("TINK_CALLBACK_URI"),
        storage=storage,
    )
    tink_balance = check_tink_account_balance(account_id, tink)
    firefly_balance = check_firefly_account_balances(account_id)
    difference = tink_balance - firefly_balance
    return {
        "Status": "OK",
        "Tink Balance": tink_balance,
        "Firefly Balance": firefly_balance,
        "Difference": difference,
    }


@app.get("/update")
def update_account(
    date_until: str = Query(
        ..., title="Date Until", description="Get data until this date"
    ),
    account_id: str = Query(
        ..., title="Account id", description="Id for the account to update"
    ),
):
    try:
        datetime.strptime(date_until, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format is not valid")
    try:
        tink = Tink(
            client_id=os.environ.get("TINK_CLIENT_ID"),
            client_secret=os.environ.get("TINK_CLIENT_SECRET"),
            redirect_uri=os.environ.get("TINK_CALLBACK_URI"),
            storage=TokenStorage(),
        )
        transactions_page = tink.transactions().get()
    except NoAuthorizationCodeException:
        link = tink.get_authorization_code_link()
    response = RedirectResponse(url=tink.get_authorization_code_link())
    response.set_cookie(key="date_until", value=date_until)
    response.set_cookie(key="account_id", value=account_id)
    return response
