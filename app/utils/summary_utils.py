from app.summary.summary import Summary


def add_transaction_to_summary(transaction):
    Summary().add(
        {
            "date": transaction["date"],
            "description": transaction["description"],
            "amount": transaction["amount"],
        }
    )
