import os
import csv
import sys
import time
from datetime import datetime
from app.storage.storage import TokenStorage
from app.summary.summary import Summary
from app.utils.utils import process_transactions_page, write_configuration_file
from tink_http_python.tink import Tink
from tink_http_python.exceptions import NoAuthorizationCodeException
from tink_http_python.transactions import Transactions

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

    if account_id is None:
        raise HTTPException(status_code=400, detail="account_id cookie not found")

    # Store the authorization code and initialize the API
    storage = TokenStorage()
    storage.store_new_authorization_code(code)

    tink = Tink(
        client_id=os.environ.get("TINK_CLIENT_ID"),
        client_secret=os.environ.get("TINK_CLIENT_SECRET"),
        redirect_uri=os.environ.get("TINK_CALLBACK_URI"),
        storage=storage,
    )

    # Create the CSV file
    page = None
    stop = False
    current_timestamp = int(time.time())
    output_path = os.environ.get("CSV_PATH")
    file_name = f"{output_path}/output_{current_timestamp}.csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f, delimiter=";")
        while not stop:
            transactions_page = tink.transactions().get(pageToken=page)
            stop = process_transactions_page(
                account_id, writer, date_until, transactions_page
            )
            page = transactions_page.next_page_token
    # Create the configuration file
    write_configuration_file(account_id, output_path, current_timestamp)
    return {"Status": "OK", "Summary": Summary().get()}


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
